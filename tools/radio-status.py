#!/usr/bin/env python3
"""Selected radio state and current-boot timeout counts; no scans or identifiers."""
import json
import os
import subprocess
from pathlib import Path


def read(path):
    try:
        return Path(path).read_text().strip()
    except OSError:
        return None


def command(args):
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=8)
        return result.stdout if result.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


controllers = []
for controller in sorted(Path('/sys/class/bluetooth').glob('hci*')):
    device = controller / 'device'
    controllers.append({'vendor': read(device / 'vendor'),
                        'device': read(device / 'device'),
                        'driver': (device / 'driver').resolve().name
                        if (device / 'driver').exists() else None})

show = command(['bluetoothctl', 'show'])
state = {}
if show is not None:
    for line in show.splitlines():
        key, separator, value = line.strip().partition(':')
        if separator and key in ('Powered', 'PowerState', 'Discovering'):
            state[key] = value.strip()

network = command(['nmcli', '-t', '-f', 'TYPE,STATE', 'device', 'status'])
network_states = []
if network is not None:
    for line in network.splitlines():
        kind, separator, status = line.partition(':')
        if separator and kind in ('wifi', 'ethernet', 'bt'):
            network_states.append({'type': kind, 'state': status})

journal = command(['journalctl', '-k', '-b', '--no-pager', '-o', 'cat'])
markers = {'set_event_mask_timeouts': 'command 0x0c01 tx timeout',
           'resume_recovery_attempts': 'recovering transport once after resume command timeout',
           'resume_recovery_failures': 'resume transport recovery failed',
           'codec_capability_errors': 'Failed to read codec capabilities (-22)'}
counts = ({key: sum(marker in line for line in journal.splitlines())
           for key, marker in markers.items()} if journal is not None else None)
print(json.dumps({'kernel': os.uname().release,
                  'controllers': controllers,
                  'default_controller_state': state if show is not None else None,
                  'network_states': network_states if network is not None else None,
                  'rfkill': [{key: read(p / key) for key in ('type', 'soft', 'hard')}
                             for p in sorted(Path('/sys/class/rfkill').glob('rfkill*'))],
                  'current_boot_journal_counts': counts,
                  'limitations': ['Controller state and management queries do not prove live HCI transport or peripheral connections.',
                                  'Journal counts cover only records accessible to this user; zero is not a full health qualification.',
                                  'Bluetooth state is for the default controller; no scanning, pairing, reset or power change is performed.']}, indent=2))
