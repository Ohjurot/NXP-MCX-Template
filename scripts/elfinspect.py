"""
Inspect the built ELF: section sizes, memory usage and biggest symbols.
Invoked via exec.bat: exec.bat elfinspect [elf] [--symbols N]
"""
import argparse
import pathlib
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).parent.parent
TOOLS_DIR = REPO_ROOT / 'env' / 'tools'
BUILD_DIR = REPO_ROOT / 'build'
GCC_BIN   = TOOLS_DIR / 'arm-gnu-toolchain' / 'bin'


def _tool(name):
    p = GCC_BIN / f'arm-none-eabi-{name}.exe'
    if not p.exists():
        sys.exit(f'[elfinspect] arm-none-eabi-{name} not found in env/tools — run exec.bat first')
    return str(p)


def _run(args):
    return subprocess.check_output([str(a) for a in args], text=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('elf', nargs='?', default=BUILD_DIR / 'firmware.elf', type=pathlib.Path)
    parser.add_argument('--symbols', type=int, default=20, help='number of biggest symbols to show')
    args = parser.parse_args()

    if not args.elf.exists():
        sys.exit(f'[elfinspect] {args.elf} not found — run exec.bat build first')

    print(f'[elfinspect] {args.elf}\n')

    print('=== ELF header ===')
    header = _run([_tool('readelf'), '-h', args.elf])
    for line in header.splitlines():
        if any(key in line for key in ('Entry point', 'Machine', 'Type:', 'Flags')):
            print(line)
    print()

    print('=== Size (Berkeley) ===')
    print(_run([_tool('size'), args.elf]))

    print('=== Sections (sysv) ===')
    print(_run([_tool('size'), '--format=sysv', args.elf]))

    print(f'=== Top {args.symbols} symbols by size ===')
    nm = _run([_tool('nm'), '--print-size', '--size-sort', '--radix=d', args.elf])
    for line in nm.splitlines()[-args.symbols:][::-1]:
        print(line)
