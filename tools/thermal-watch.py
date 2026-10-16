#!/usr/bin/env python3
"""Read thermal-zone and labelled SMC temperatures; never apply a load or tuning."""
import argparse
import json
import math
import sys
import time
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--seconds', type=float, default=10)
parser.add_argument('--interval', type=float, default=1)
args = parser.parse_args()
if (not math.isfinite(args.seconds) or not math.isfinite(args.interval)
        or not 0 < args.seconds <= 300 or not .25 <= args.interval <= 60):
    parser.error('seconds must be in (0, 300]; interval must be in [0.25, 60]')

hwmon = next((p for p in Path('/sys/class/hwmon').glob('hwmon*')
              if (p / 'name').read_text().strip() == 'macsmc_hwmon'), None)
zone = next((p for p in Path('/sys/class/thermal').glob('thermal_zone*')
             if (p / 'type').read_text().strip() == 'macsmc_soc_die'), None)
if hwmon is None or zone is None:
    sys.exit('SMC die thermal zone is absent; no fallback or synthetic value is used.')
channels = {p.read_text().strip(): p.with_name(p.name.replace('_label', '_input'))
            for p in hwmon.glob('temp*_label')
            if p.read_text().startswith('SoC die ')}
started = time.monotonic()
try:
    while time.monotonic() - started < args.seconds:
        values = {k: int(p.read_text()) / 1000 for k, p in channels.items()}
        temperature = int((zone / 'temp').read_text()) / 1000
        if not values or any(not -40 <= v <= 150 for v in [temperature, *values.values()]):
            sys.exit('Missing or implausible temperature; stopping.')
        print(json.dumps(dict(elapsed_s=round(time.monotonic() - started, 2),
                              zone_C=temperature, channels_C=values)), flush=True)
        time.sleep(args.interval)
except (OSError, ValueError) as error:
    sys.exit(f'Sensor read failed; no cached value substituted: {error}')
except KeyboardInterrupt:
    pass
