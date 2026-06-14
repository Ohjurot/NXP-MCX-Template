"""
Build the firmware project (device selection comes from config.yaml).
Invoked via exec.bat: exec.bat build [--clean] [--jobs N]
"""
import argparse
import os
import pathlib
import shutil
import subprocess
import sys

import yaml

REPO_ROOT = pathlib.Path(__file__).parent.parent
TOOLS_DIR = REPO_ROOT / 'env' / 'tools'
SRC_DIR   = REPO_ROOT / 'src'
BUILD_DIR = REPO_ROOT / 'build'
CMAKE_DIR = REPO_ROOT / 'cmake'

CONFIG = yaml.safe_load((REPO_ROOT / 'config.yaml').read_text())


def _find(rel, dirs):
    for d in dirs:
        p = d / rel
        if p.exists():
            return p
    return None


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--clean', action='store_true')
    parser.add_argument('--jobs',  type=int, default=os.cpu_count())
    args = parser.parse_args()

    cmake = _find('bin/cmake.exe',              [TOOLS_DIR / 'cmake'])
    ninja = _find('ninja.exe',                  [TOOLS_DIR / 'ninja'])
    gcc   = _find('bin/arm-none-eabi-gcc.exe',  [TOOLS_DIR / 'arm-gnu-toolchain'])

    for name, val in (('cmake', cmake), ('ninja', ninja), ('arm-none-eabi-gcc', gcc)):
        if val is None:
            sys.exit(f'[build] {name} not found in env/tools — run exec.bat first')

    env = os.environ.copy()
    env['PATH'] = str(gcc.parent) + os.pathsep + str(ninja.parent) + os.pathsep + env.get('PATH', '')

    if args.clean and BUILD_DIR.exists():
        print(f'[build] Cleaning {BUILD_DIR}')
        shutil.rmtree(BUILD_DIR)
    BUILD_DIR.mkdir(exist_ok=True)

    subprocess.check_call([
        str(cmake),
        f'-DCMAKE_TOOLCHAIN_FILE={CMAKE_DIR / "toolchain-arm-none-eabi.cmake"}',
        f'-DCMAKE_MAKE_PROGRAM={ninja}',
        f'-Ddevice={CONFIG["device"]}',
        f'-Dlinker_script_path={CONFIG["linker_script_path"]}',
        '-G', 'Ninja',
        '-DCMAKE_BUILD_TYPE=MinSizeRel',
        '-B', str(BUILD_DIR),
        '-S', str(SRC_DIR),
    ], env=env)

    subprocess.check_call([
        str(cmake), '--build', str(BUILD_DIR), '--parallel', str(args.jobs),
    ], env=env)

    print(f'[build] Output: {BUILD_DIR}')
