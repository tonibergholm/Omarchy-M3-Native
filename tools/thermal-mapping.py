#!/usr/bin/env python3
"""Verify J613 indexed thermal sensor mapping; read-only, selected output only.

Default /sys/firmware/fdt needs root read access. --dtb checks a supplied DTB
instead and makes no claim about the running kernel. Requires python-libfdt.
"""
import argparse
import json
from pathlib import Path
import struct
import sys

EXPECTED = dict(zip(
    ['cpu-e0-thermal', 'cpu-e1-thermal', 'cpu-p0-thermal',
     'cpu-p1-thermal', 'cpu-p2-thermal', 'cpu-p3-thermal'],
    ['Te05', 'Te0P', 'Tp05', 'Tp0L', 'Tp0b', 'Tp0r']))


def inspect(data):
    import libfdt
    fdt = libfdt.Fdt(data)
    if b'apple,j613\0' not in bytes(fdt.getprop(0, 'compatible')):
        raise ValueError('This verifier is scoped to J613 only')
    hwmon = fdt.path_offset('/soc/smc@2ec400000/hwmon')
    provider = int.from_bytes(bytes(fdt.getprop(hwmon, 'phandle')), 'big')
    keys = []
    node = fdt.first_subnode(hwmon, quiet=(libfdt.NOTFOUND,))
    while node >= 0:
        if fdt.get_name(node).startswith('temperature-'):
            keys.append(bytes(fdt.getprop(node, 'apple,key-id')).rstrip(b'\0').decode())
        node = fdt.next_subnode(node, quiet=(libfdt.NOTFOUND,))
    zones = []
    for name, expected in EXPECTED.items():
        zone = fdt.path_offset('/thermal-zones/' + name)
        reference, index = struct.unpack('>II', bytes(fdt.getprop(zone, 'thermal-sensors')))
        if reference != provider:
            raise ValueError('Unexpected thermal sensor provider for ' + name)
        key = keys[index]
        zones.append(dict(zone=name, index=index, key=key,
                          expected_key=expected, matches=(key == expected)))
    return dict(board='J613 / T8122', zones=zones,
                mapping_matches=all(z['matches'] for z in zones),
                scope='DT sensor indices; not calibration or cooling qualification')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dtb', type=Path, default=Path('/sys/firmware/fdt'))
    args = parser.parse_args()
    try:
        result = inspect(args.dtb.read_bytes())
    except Exception as error:
        parser.exit(2, f'Cannot verify mapping: {error}\n')
    result['source'] = 'booted FDT' if args.dtb == Path('/sys/firmware/fdt') else 'supplied DTB'
    print(json.dumps(result, indent=2))
    return 0 if result['mapping_matches'] else 1


if __name__ == '__main__':
    sys.exit(main())
