#!/usr/bin/env python3
"""Read selected power state; --watch records logind sleep signals without inhibiting sleep."""
import argparse
import json
import os
import signal
import time
import uuid
from pathlib import Path


def read(path):
    try:
        return Path(path).read_text().strip()
    except OSError:
        return None


def snapshot(phase):
    battery = Path('/sys/class/power_supply/macsmc-battery')
    return {'phase': phase, 'epoch_s': time.time(),
            'boottime_s': time.clock_gettime(time.CLOCK_BOOTTIME),
            'monotonic_s': time.monotonic(), 'kernel': os.uname().release,
            'battery': {key: read(battery / key) for key in
                        ('status', 'capacity', 'charge_now', 'energy_now',
                         'energy_full', 'power_now', 'voltage_now')},
            'external_power': [read(p / 'online') for p in
                               sorted(Path('/sys/class/power_supply').iterdir())
                               if (p / 'online').exists()],
            'screen': read('/sys/class/backlight/apple-panel-bl/brightness'),
            'keyboard': read('/sys/class/leds/kbd_backlight/brightness'),
            'success': read('/sys/power/suspend_stats/success'),
            'fail': read('/sys/power/suspend_stats/fail')}


class Recorder:
    def __init__(self, output):
        # Exclusive creation prevents silently combining separate observer runs.
        self.fd = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                          os.O_NOFOLLOW, 0o600)
        os.fchmod(self.fd, 0o600)
        self.file = os.fdopen(self.fd, 'w')
        self.run = uuid.uuid4().hex
        self.cycle = 0
        self.pre = None

    def write(self, row):
        row = dict(row, observer_run=self.run, cycle=self.cycle)
        self.file.write(json.dumps(row) + '\n')
        self.file.flush()
        os.fsync(self.file.fileno())

    def transition(self, sleeping):
        row = snapshot('prepare-for-sleep' if sleeping else 'resume-signal')
        if sleeping:
            self.cycle += 1
            row['replaces_unmatched_pre'] = self.pre is not None
            self.pre = row.copy()
        else:
            row['matched_pre'] = self.pre is not None
            if self.pre is not None:
                row['clock_suspended_seconds'] = (
                    row['boottime_s'] - self.pre['boottime_s'] -
                    (row['monotonic_s'] - self.pre['monotonic_s']))
            self.pre = None
        self.write(row)
        return row

    def close(self):
        self.file.close()


def watch(output):
    # Import desktop D-Bus bindings only for explicit monitoring.
    from gi.repository import Gio, GLib
    recorder = Recorder(output)
    loop = GLib.MainLoop()
    bus = Gio.bus_get_sync(Gio.BusType.SYSTEM, None)
    timers = []
    failures = []
    resume_at = None

    def guarded(callback):
        def call(*args):
            try:
                return callback(*args)
            except Exception as error:
                failures.append(type(error).__name__)
                loop.quit()
                return GLib.SOURCE_REMOVE
        return call

    def delayed(seconds):
        row = snapshot('post-' + str(seconds) + 's')
        row['seconds_since_resume_signal'] = row['monotonic_s'] - resume_at
        recorder.write(row)
        return GLib.SOURCE_REMOVE

    def changed(connection, sender, path, interface, member, parameters, data):
        nonlocal timers, resume_at
        values = parameters.unpack()
        if len(values) != 1 or not isinstance(values[0], bool):
            return
        for timer in timers:
            GLib.source_remove(timer)
        timers = []
        sleeping = values[0]
        row = recorder.transition(sleeping)
        resume_at = None if sleeping else row['monotonic_s']
        if not sleeping:
            for seconds in (30, 60, 120):
                # Remove completed IDs so later sleeps never remove reused IDs.
                holder = []
                def fire(seconds=seconds, holder=holder):
                    if holder[0] in timers:
                        timers.remove(holder[0])
                    return delayed(seconds)
                timer = GLib.timeout_add_seconds(seconds, guarded(fire))
                holder.append(timer)
                timers.append(timer)

    subscription = bus.signal_subscribe(
        'org.freedesktop.login1', 'org.freedesktop.login1.Manager',
        'PrepareForSleep', '/org/freedesktop/login1', None,
        Gio.DBusSignalFlags.NONE, guarded(changed), None)
    recorder.write(snapshot('observer-start'))
    signal.signal(signal.SIGTERM, lambda *_: loop.quit())
    signal.signal(signal.SIGINT, lambda *_: loop.quit())
    try:
        loop.run()
    finally:
        for timer in timers:
            GLib.source_remove(timer)
        bus.signal_unsubscribe(subscription)
        try:
            recorder.write(snapshot('observer-stop'))
        finally:
            recorder.close()
    if failures:
        raise RuntimeError('Observer callback failed: ' + failures[0])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--watch', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.watch:
        if args.output is None:
            parser.error('--watch requires a new --output file in an existing private directory')
        watch(args.output)
    elif args.output is not None:
        parser.error('--output requires --watch')
    else:
        print(json.dumps(snapshot('snapshot'), indent=2))


if __name__ == '__main__':
    main()
