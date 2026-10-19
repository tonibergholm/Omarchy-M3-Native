#!/usr/bin/env python3
"""Read-only J613 speaker-rate/PCM timing recorder; no audio stream is opened."""
import argparse
import ctypes as c
import json
import os
import time
from pathlib import Path

class Control:

    def __init__(self):
        self.lib = c.CDLL('libasound.so.2')
        self.ctl = c.c_void_p()
        self.ident = c.c_void_p()
        self.value = c.c_void_p()
        ptr = c.c_void_p
        signatures = [('snd_ctl_open', [c.POINTER(ptr), c.c_char_p, c.c_int], c.c_int),
                      ('snd_ctl_elem_id_malloc', [c.POINTER(ptr)], c.c_int),
                      ('snd_ctl_elem_value_malloc', [c.POINTER(ptr)], c.c_int),
                      ('snd_ctl_elem_id_set_interface', [ptr, c.c_int], None),
                      ('snd_ctl_elem_id_set_name', [ptr, c.c_char_p], None),
                      ('snd_ctl_elem_value_set_id', [ptr, ptr], None),
                      ('snd_ctl_elem_read', [ptr, ptr], c.c_int),
                      ('snd_ctl_elem_value_get_integer', [ptr, c.c_uint], c.c_long),
                      ('snd_ctl_elem_value_free', [ptr], None),
                      ('snd_ctl_elem_id_free', [ptr], None),
                      ('snd_ctl_close', [ptr], c.c_int)]
        for name, args, result in signatures:
            fn = getattr(self.lib, name)
            fn.argtypes = args
            fn.restype = result
        try:
            for result in [self.lib.snd_ctl_open(c.byref(self.ctl), b'hw:AppleJ613', 0), self.lib.snd_ctl_elem_id_malloc(c.byref(self.ident)), self.lib.snd_ctl_elem_value_malloc(c.byref(self.value))]:
                if result < 0:
                    raise OSError(-result, 'ALSA allocation/open failed')
            self.lib.snd_ctl_elem_id_set_interface(self.ident, 2)
            self.lib.snd_ctl_elem_id_set_name(self.ident, b'Speaker Sample Rate')
            self.lib.snd_ctl_elem_value_set_id(self.value, self.ident)
        except BaseException:
            self.close()
            raise

    def rate(self):
        result = self.lib.snd_ctl_elem_read(self.ctl, self.value)
        if result < 0:
            raise OSError(-result, 'ALSA control read failed')
        return self.lib.snd_ctl_elem_value_get_integer(self.value, 0)

    def close(self):
        if self.value:
            self.lib.snd_ctl_elem_value_free(self.value)
            self.value = c.c_void_p()
        if self.ident:
            self.lib.snd_ctl_elem_id_free(self.ident)
            self.ident = c.c_void_p()
        if self.ctl:
            self.lib.snd_ctl_close(self.ctl)
            self.ctl = c.c_void_p()

def read(path):
    try:
        return path.read_text().strip()
    except OSError:
        return None

def pcm(card, name):
    base = card / name / 'sub0'
    status = read(base / 'status')
    params = read(base / 'hw_params')
    out = {}
    if status is not None:
        for line in status.splitlines():
            key, _, value = line.partition(':')
            if key.strip() in ('state', 'hw_ptr', 'appl_ptr', 'delay', 'avail'):
                out[key.strip()] = value.strip()
        if not out:
            out['state'] = status
    if params is not None:
        for line in params.splitlines():
            key, _, value = line.partition(':')
            if key in ('rate', 'channels', 'format'):
                out[key] = value.strip()
        if params == 'closed':
            out['params'] = 'closed'
    return out

def notify_ready():
    import socket
    address = os.environ['NOTIFY_SOCKET']
    if address.startswith('@'):
        address = '\0' + address[1:]
    with socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as connection:
        connection.connect(address)
        connection.sendall(b'READY=1')

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--duration', type=float, default=60)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--notify-ready', action='store_true',
                   help='Notify systemd after saving the first sample')
    args = p.parse_args()
    if args.notify_ready and not os.environ.get('NOTIFY_SOCKET'):
        p.error('--notify-ready requires NOTIFY_SOCKET')
    if not 0 < args.duration <= 60:
        p.error('duration must be >0 and <=60 seconds')
    if b'apple,j613\x00' not in Path('/sys/firmware/devicetree/base/compatible').read_bytes():
        p.error('J613 only')
    ctl = None
    card = None
    start = time.monotonic()
    next_sample = start
    count = 0
    fd = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'w', buffering=1) as output:
        try:
            while time.monotonic() - start < args.duration:
                row = {'monotonic_s': time.monotonic(), 'boottime_s': time.clock_gettime(time.CLOCK_BOOTTIME)}
                if card is None:
                    card = next((v.parent for v in Path('/proc/asound').glob('card*/id') if read(v) == 'AppleJ613'), None)
                if card is not None:
                    try:
                        if ctl is None:
                            ctl = Control()
                        row['speaker_rate_Hz'] = ctl.rate()
                    except OSError as error:
                        row['control_error_errno'] = error.errno
                    row['speaker_pcm'] = pcm(card, 'pcm1p')
                    row['sense_pcm'] = pcm(card, 'pcm2c')
                else:
                    row['card'] = 'not-yet-present'
                output.write(json.dumps(row) + '\n')
                if count == 0 and args.notify_ready:
                    notify_ready()
                count += 1
                next_sample += 0.1
                time.sleep(max(0, next_sample - time.monotonic()))
        finally:
            if ctl is not None:
                ctl.close()
    print(json.dumps({'samples': count, 'duration_s': time.monotonic() - start, 'output_created': True}))
if __name__ == '__main__':
    main()
