#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""CI-only compile check. Never installs or loads the generated modules."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import platform
import shutil
import struct
import subprocess
import tarfile
import time
from urllib.request import urlopen

assert os.environ.get('GITHUB_ACTIONS') == 'true', 'Run only in disposable GitHub CI'
assert platform.machine() == 'aarch64', 'Matching SDK host tools require ARM64'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--work', type=Path, required=True)
args = parser.parse_args()
work = args.work.resolve()
work.mkdir(parents=True, exist_ok=False)
repo = Path(__file__).resolve().parents[2]
revision = 'c46d7dcdb8712ea9aeb0ce47b439ffae76371e55'
release = 'https://github.com/omacom/linux-aurora/releases/download/aurora-2026.10.17.20/'
kernel = '7.1.12-2-20261017.20-sep-ARCH'
archives = {
    f'aurora-linux-{revision}.tar.gz': '493ed9fb4a9e245fd59a92a2396d3c968516be932749b8059757a29380652509',
    'linux-aurora-headers-7.1.12.aurora2-20261017.20-aarch64.pkg.tar.zst': '7d8e7370fbc777e8694f29b66e20bf60eb826432234824833ac28ebdf4bee5f8',
}
result = {
    'scope': 'Full appledrm external-module compilation only; no install/load/native output test',
    'source_commit': revision,
    'sdk_kernel': kernel,
    'runner_arch': platform.machine(),
    'compiler': subprocess.check_output(['clang', '--version'], text=True).splitlines()[0],
    'pahole_version': subprocess.check_output(['pahole', '--version'], text=True).strip(),
    'pahole_source_commit': subprocess.check_output(['git', '-C', str(Path(os.environ['RUNNER_TEMP']) / 'pahole-source'), 'rev-parse', 'HEAD'], text=True).strip(),
    'pahole_libbpf_commit': subprocess.check_output(['git', '-C', str(Path(os.environ['RUNNER_TEMP']) / 'pahole-source/lib/bpf'), 'rev-parse', 'HEAD'], text=True).strip(),
    'archives': archives,
    'builds': [],
}
assert result['pahole_version'] == 'v1.32'
assert result['pahole_source_commit'] == 'fa725d687ce3a712ef296b46bc63ea57ef466014'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def apply(source, patch):
    subprocess.run(['git', 'apply', '--check', str(patch)], cwd=source, check=True)
    subprocess.run(['git', 'apply', str(patch)], cwd=source, check=True)

try:
    for name, digest in archives.items():
        destination = work / name
        with urlopen(release + name, timeout=60) as response, destination.open('wb') as output:
            shutil.copyfileobj(response, output)
        assert sha(destination) == digest, f'Archive digest mismatch: {name}'

    source = work / 'reference'
    source.mkdir()
    prefix = 'drivers/gpu/drm/apple/'
    with tarfile.open(work / f'aurora-linux-{revision}.tar.gz', 'r|gz') as archive:
        for member in archive:
            parts = member.name.split('/', 1)
            if len(parts) != 2 or not parts[1].startswith(prefix):
                continue
            if member.isdir():
                continue
            assert member.isfile() and '..' not in Path(parts[1]).parts
            destination = source / parts[1]
            destination.parent.mkdir(parents=True, exist_ok=True)
            with archive.extractfile(member) as data, destination.open('wb') as output:
                shutil.copyfileobj(data, output)

    brightness = repo / 'patches/j613-v14-backlight-candidate.patch'
    colors = repo / 'patches/aurora20-external-sdr-colorimetry-candidate.patch'
    apply(source, brightness)
    brightness_hashes = {
        'iomfb_v14_7.c': 'aed10fb4f74f07032f8d4c05f7e5eee4023b8346ee61cc2f3863318131cf5d03',
        'iomfb_v14_7_swap.h': '86451a3e0e644959e563770f04ffcadc4c428a650c45a101a913c54b8dcd36a2',
    }
    for name, digest in brightness_hashes.items():
        assert sha(source / prefix / name) == digest, f'Retained brightness source mismatch: {name}'
    result['retained_brightness_source_hashes'] = brightness_hashes
    result['patches'] = {p.name: sha(p) for p in [brightness, colors]}
    candidate = work / 'candidate'
    shutil.copytree(source, candidate)
    apply(candidate, colors)
    candidate_hashes = {
        'dcp-internal.h': 'a83a164de370825221e0119e371b69b880b63e9522e55499f00a4f8bbdd539ad',
        'dcp.c': 'd68ec655998b3c7156e283fa11e918fc5f00da45b05fa119d7be60546549c2b7',
        'iomfb_template.c': 'c04f10ad6d0f4b29ddad8b8a979c43d12a2eb97aec68162521ad179314508f58',
        'parser.c': '2edaccdb280081f38dfb3a2b7eb5cf9612ceb5cccfdf4fce0cfe6a1cc267ab1b',
        'plane.c': '5a8feca7225386c1227ea2f51087292fc34b02e4f9e5632d7e5ceee37e4800e2',
    }
    for name, digest in candidate_hashes.items():
        assert sha(candidate / prefix / name) == digest, f'Backport source mismatch: {name}'
    result['candidate_source_hashes_before_alignment_prerequisite'] = dict(candidate_hashes)
    alignment = repo / 'patches/aurora20-parser-unaligned-source-type.patch'
    apply(candidate, alignment)
    candidate_hashes['parser.c'] = '91775654d398284ba5f7d970de462711317243a7aa1fe29bb20937d1b92fdbe6'
    assert sha(candidate / prefix / 'parser.c') == candidate_hashes['parser.c']
    result['patches'][alignment.name] = sha(alignment)
    result['candidate_source_hashes'] = candidate_hashes

    sdk_root = work / 'sdk'
    sdk_root.mkdir()
    subprocess.run(['tar', '--zstd', '-xf', str(work / next(n for n in archives if n.endswith('.zst'))), '-C', str(sdk_root)], check=True)
    sdk = sdk_root / 'usr/lib/modules' / kernel / 'build'
    assert (sdk / 'Module.symvers').is_file()
    assert (sdk / 'include/config/kernel.release').read_text().strip() == kernel
    result['sdk_config_sha256'] = sha(sdk / '.config')
    environment = dict(os.environ, ARCH='arm64', LLVM='1')
    for name in ['reference', 'candidate']:
        driver = work / name / 'drivers/gpu/drm/apple'
        log = work / f'{name}-build.log'
        started = time.monotonic()
        with log.open('w') as output:
            build = subprocess.run(['make', '-C', str(sdk), f'M={driver}', 'W=1', '-j2', 'modules'], env=environment, stdout=output, stderr=subprocess.STDOUT, timeout=300)
        entry = {'variant': name, 'exit_code': build.returncode, 'elapsed_s': round(time.monotonic() - started, 3), 'diagnostic_warning_lines': [line for line in log.read_text().splitlines() if 'warning:' in line.lower()]}
        result['builds'].append(entry)
        if build.returncode:
            print(log.read_text()[-6000:], flush=True)
        assert build.returncode == 0, f'{name} module build failed'
        module = driver / 'appledrm.ko'
        header = module.read_bytes()[:20]
        assert header[:6] == b'\x7fELF\x02\x01' and struct.unpack('<H', header[18:20])[0] == 183
        vermagic = subprocess.check_output(['modinfo', '-F', 'vermagic', str(module)], text=True).strip()
        assert vermagic.startswith(kernel + ' ')
        entry.update({'module_sha256': sha(module), 'module_architecture': 'ELF64 little-endian AArch64', 'vermagic': vermagic, 'module_size': module.stat().st_size})
        print(json.dumps(entry), flush=True)
    result['success'] = True
finally:
    (work / 'build-result.json').write_text(json.dumps(result, indent=2) + '\n')
