#!/usr/bin/env python3
"""Read selected Linux platform facts without exposing per-device identifiers."""
import json
import platform
import subprocess
from pathlib import Path


def read(path):
    try:
        return Path(path).read_bytes().rstrip(b'\0\n').decode().replace('\0', ', ')
    except (OSError, UnicodeError):
        return None


dt = Path('/sys/firmware/devicetree/base')
report = {
    'kernel': platform.release(),
    'model': read(dt / 'model'),
    'compatible': read(dt / 'compatible'),
    'firmware': {name: read(dt / 'chosen' / name) for name in (
        'asahi,os-fw-version', 'asahi,system-fw-version',
        'asahi,m1n1-stage1-version', 'asahi,m1n1-stage2-version')},
    'sep_bio_present': Path('/dev/sep-bio').exists(),
    'thermal_zones': [dict(type=read(z / 'type'), temperature_mC=read(z / 'temp'))
                      for z in sorted(Path('/sys/class/thermal').glob('thermal_zone*'))],
    'cpu_policies': [dict(driver=read(p / 'scaling_driver'),
                          governor=read(p / 'scaling_governor'),
                          min_kHz=read(p / 'scaling_min_freq'),
                          max_kHz=read(p / 'scaling_max_freq'))
                     for p in sorted(Path('/sys/devices/system/cpu/cpufreq').glob('policy*'))],
    'cpu0_idle': [dict(name=read(p / 'name'), disabled=read(p / 'disable'),
                       usage=read(p / 'usage')) for p in
                  sorted(Path('/sys/devices/system/cpu/cpu0/cpuidle').glob('state*'))],
    'backlights': sorted(p.name for p in Path('/sys/class/backlight').glob('*')),
    'keyboard_brightness': read('/sys/class/leds/kbd_backlight/brightness'),
}
packages = ['linux-aurora', 'm1n1-aurora', 'mesa-m3', 'libfprint', 'fprintd',
            'aurora-touchid', 'omarchy-dev', 'omarchy-mac']
try:
    result = subprocess.run(['pacman', '-Q', *packages], text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                            timeout=10, check=False)
    report['packages'] = result.stdout.splitlines()
except (OSError, subprocess.TimeoutExpired):
    report['packages'] = None
print(json.dumps(report, indent=2))
