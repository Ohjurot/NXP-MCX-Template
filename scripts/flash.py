"""
Flash the built ELF with NXP LinkServer.
Invoked via exec.bat: exec.bat flash [elf] [--device D]
"""
import argparse
import os
import pathlib
import re
import shutil
import subprocess
import sys

import yaml

REPO_ROOT = pathlib.Path(__file__).parent.parent
BUILD_DIR = REPO_ROOT / 'build'

CONFIG = yaml.safe_load((REPO_ROOT / 'config.yaml').read_text())


def _find_linkserver():
    # Default install location: <system drive>\nxp\LinkServer_<version>\LinkServer.exe
    # Multiple versions may be installed side by side; pick the latest.
    sysdrive = os.environ.get('SystemDrive', 'C:')
    candidates = []
    for d in pathlib.Path(sysdrive + '\\').glob('nxp/LinkServer_*'):
        exe = d / 'LinkServer.exe'
        if exe.exists():
            version = tuple(int(n) for n in re.findall(r'\d+', d.name))
            candidates.append((version, exe))
    if candidates:
        return max(candidates)[1]

    # Fallback: LinkServer on PATH
    exe = shutil.which('LinkServer')
    return pathlib.Path(exe) if exe else None


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('elf', nargs='?', default=BUILD_DIR / 'firmware.elf', type=pathlib.Path)
    parser.add_argument('--device', default=CONFIG['linkserver_device'], help='LinkServer device:board name')
    args = parser.parse_args()

    linkserver = _find_linkserver()
    if linkserver is None:
        sys.exit('[flash] LinkServer not found — install it from nxp.com (see README, "Flashing")')

    if not args.elf.exists():
        sys.exit(f'[flash] {args.elf} not found — run exec.bat build first')

    print(f'[flash] Using {linkserver}')
    subprocess.check_call([
        str(linkserver), 'flash', args.device, 'load', str(args.elf),
    ])
