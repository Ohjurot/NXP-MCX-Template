"""
Environment setup file
"""
import os
import sys
import pathlib
import subprocess
import urllib.request
import zipfile
import shutil


def _dl_progress(count, block, total):
    if total > 0:
        print(f'\r  {min(100, count * block * 100 // total):3d}%  {count * block / 1048576:.1f} MB', end='', flush=True)


def _download(url, dest):
    urllib.request.urlretrieve(url, dest, reporthook=_dl_progress)
    print()


def _unzip(src, dest, strip_root=True):
    dest.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(src) as zf:
        for m in zf.infolist():
            parts = pathlib.PurePosixPath(m.filename).parts
            rel   = pathlib.Path(*(parts[1:] if strip_root and len(parts) > 1 else parts))
            tgt   = dest / rel
            if m.is_dir():
                tgt.mkdir(parents=True, exist_ok=True)
            else:
                tgt.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(m) as s, open(tgt, 'wb') as d:
                    shutil.copyfileobj(s, d)


def _ensure_tool(label, url, dest, marker, strip_root=True):
    if (dest / marker).exists():
        return
    print(f'Downloading {label}...')
    tmp = dest.parent / f'_dl_{dest.name}.zip'
    try:
        _download(url, tmp)
        _unzip(tmp, dest, strip_root)
    finally:
        if tmp.exists():
            tmp.unlink()


def _ensure_sdk(python_bin, vendor_dir):
    west_cfg = vendor_dir / '.west' / 'config'

    if not west_cfg.exists():
        subprocess.check_call((
            str(python_bin), '-m', 'west', 'init', '-l', 'mcuxsdk-manifests',
        ), cwd=str(vendor_dir))

        # Minimal set needed for bare-metal builds
        subprocess.check_call((
            str(python_bin), '-m', 'west', 'update',
            'core',               # SDK drivers, cmake/Kconfig infrastructure
            'CMSIS',              # core_cm7.h etc.
            'mcu-sdk-components', # serial manager, uart adapter, debug console
            'mcux-devices-rt',    # MIMXRT device headers, startup, linker scripts
            'mcux-devices-mcx',   # MCX device headers, startup, linker scripts (MCXA266)
        ), cwd=str(vendor_dir))


if __name__ == '__main__':
    base_dir = pathlib.Path(__file__).parent
    venv_dir = base_dir / 'env'
    python_bin = venv_dir / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')

    # Create venv
    if not python_bin.exists():
        subprocess.check_call((
            sys.executable,
            '-m',
            'venv',
            str(venv_dir)
        ))

        # Install requirements
        requirements = base_dir / 'requirements.txt'
        subprocess.check_call((
            str(python_bin),
            '-m',
            'pip',
            'install',
            '-r',
            str(requirements)
        ))

    # NXP SDK + dependencies via west
    _ensure_sdk(python_bin, base_dir.parent / 'vendor')

    # Portable build tools
    tools_dir = base_dir / 'tools'
    tools_dir.mkdir(parents=True, exist_ok=True)

    _ensure_tool(
        'ARM GNU Toolchain 14.2.Rel1',
        'https://github.com/xpack-dev-tools/arm-none-eabi-gcc-xpack'
        '/releases/download/v14.2.1-1.1/xpack-arm-none-eabi-gcc-14.2.1-1.1-win32-x64.zip',
        tools_dir / 'arm-gnu-toolchain', 'bin/arm-none-eabi-gcc.exe',
    )

    _ensure_tool(
        'CMake 3.31.6',
        'https://github.com/Kitware/CMake/releases/download/v3.31.6/cmake-3.31.6-windows-x86_64.zip',
        tools_dir / 'cmake', 'bin/cmake.exe',
    )

    _ensure_tool(
        'Ninja 1.12.1',
        'https://github.com/ninja-build/ninja/releases/download/v1.12.1/ninja-win.zip',
        tools_dir / 'ninja', 'ninja.exe', strip_root=False,
    )
