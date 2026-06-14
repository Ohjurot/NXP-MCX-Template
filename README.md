# NXP MCU Build Template

Self-contained, IDE-free build template for NXP microcontrollers based on the
[MCUXpresso SDK](https://github.com/nxp-mcuxpresso/mcuxsdk-manifests) (west workspace),
CMake and Ninja. A single `exec.bat` call bootstraps everything — Python venv, SDK
checkout and portable toolchain — no globally installed tools required besides Python and Git.

## Targets

| Family | Status |
|---|---|
| MCX (tested on FRDM-MCXA266) | ✅ Working |
| i.MX RT crossover MCUs | 🔜 Planned (device files already fetched) |
| i.MX application processors — realtime cores (Cortex-M alongside Linux) | 🔜 Planned |

Currently the repository contains **one single project** (`src/`). See [Roadmap](#roadmap)
for the planned multi-project / dual-core layout.

> **Note:** The bootstrap currently downloads Windows binaries only (`exec.bat`,
> `.exe` tool archives). Linux/macOS support would need a small launcher + URL additions
> in `env/env.py`.

## Requirements

The bootstrap pulls the compiler, CMake and Ninja itself — these only have to be
on the development machine:

| Tool | Required | Purpose |
|---|---|---|
| Windows | Yes | The bootstrap currently ships Windows binaries only (see note above). |
| [Python 3](https://www.python.org/) | Yes | Runs the bootstrap and build scripts; provides the venv (`PATH`). |
| [Git](https://git-scm.com/) | Yes | Clones the repo and submodule, drives the west SDK checkout (`PATH`). |
| [Visual Studio Code](https://code.visualstudio.com/) | Optional | Editing, IntelliSense and the build/flash tasks (see [VS Code integration](#vs-code-integration)). The build itself works from any terminal. |
| [NXP LinkServer](https://www.nxp.com/design/design-center/software/development-software/mcuxpresso-software-and-tools-/linkserver-for-microcontrollers:LINKERSERVER) | For flashing | Programs/debugs the target via the on-board MCU-Link probe (see [Flashing](#flashing)). Not bootstrapped — install manually. |
| [MCUXpresso Config Tools](https://www.nxp.com/design/design-center/software/development-software/mcuxpresso-software-and-tools-/mcuxpresso-config-tools-pins-clocks-and-peripherals:MCUXpresso-Config-Tools) | Only to change pin/clock config | Regenerates `src/board/` from the `.mex` file. Not needed for normal builds; only when editing pin mux / clocks / peripherals (see [Adapting to another device](#adapting-to-another-device)). |

Building requires only the **Yes** rows. LinkServer and Config Tools are NXP
tools installed on demand; the bundled ARM toolchain, CMake and Ninja are
downloaded automatically into `env/tools/`.

## Quick start

```bat
git clone --recurse-submodules <repo-url>
cd <repo>
exec.bat build
```

The first run takes a while — it bootstraps the full environment:

1. Creates a Python venv in `env/env/` and installs `env/requirements.txt` (west, PyYAML).
2. Initializes a west workspace in `vendor/` from the `mcuxsdk-manifests` submodule and
   fetches the minimal SDK set: `core`, `CMSIS`, `mcu-sdk-components`,
   `mcux-devices-rt`, `mcux-devices-mcx`.
3. Downloads portable tools into `env/tools/` (nothing is installed system-wide):
   - ARM GNU Toolchain 14.2.Rel1 (xPack)
   - CMake 3.31.6
   - Ninja 1.12.1

Subsequent runs skip everything that is already present.

## Usage

`exec.bat <script> [args...]` runs `scripts/<script>.py` inside the venv:

| Command | Description |
|---|---|
| `exec.bat build` | Configure (CMake/Ninja, `MinSizeRel`) and build into `build/` |
| `exec.bat build --clean` | Wipe `build/` first, then full rebuild |
| `exec.bat build --jobs N` | Limit parallel compile jobs |
| `exec.bat elfinspect` | Section sizes, memory usage and biggest symbols of the built ELF |
| `exec.bat flash` | Program the built ELF via NXP LinkServer (see [Flashing](#flashing)) |

Build outputs: `build/firmware.elf`, `.bin`, `.hex` and `firmware.map`.

## Flashing

Flashing uses NXP [LinkServer](https://www.nxp.com/design/design-center/software/development-software/mcuxpresso-software-and-tools-/linkserver-for-microcontrollers:LINKERSERVER)
(not bootstrapped by `exec.bat` — install it manually). It talks to the on-board
MCU-Link probe of the FRDM boards (and to standalone MCU-Link / LPC-Link2 probes)
via CMSIS-DAP.

1. Download and install LinkServer from the link above (default install path is
   `C:\NXP\LinkServer_<version>\`; let the installer add it to `PATH` or do so yourself).
2. Connect the board's debug USB port and flash the built ELF:

```bat
exec.bat flash
```

`scripts/flash.py` locates the newest LinkServer install under
`%SystemDrive%\nxp\LinkServer_<version>\` (falling back to `PATH`) and runs the
flash command below. The device name comes from `linkserver_device` in
`config.yaml`; override it once with `exec.bat flash --device <name>`, or invoke
LinkServer directly:

```bat
LinkServer flash MCXA266:FRDM-MCXA266 load build\firmware.elf
```

Useful commands:

| Command | Description |
|---|---|
| `LinkServer probes` | List connected debug probes |
| `LinkServer devices` | List supported device:board names |
| `LinkServer flash <device> load <file>` | Program an `.elf`/`.hex`/`.bin` |
| `LinkServer flash <device> erase` | Mass-erase the part |
| `LinkServer gdbserver <device>` | Start a GDB server for debugging |

For another device, replace the `<device>` argument with the matching entry from
`LinkServer devices` (e.g. an `MIMXRT...` name for i.MX RT parts).

## Project layout

```
exec.bat                  Launcher: bootstraps env, runs scripts/<name>.py
config.yaml               Global device/board configuration (SDK device, linker script, LinkServer name)
env/
  env.py                  Bootstrap: venv, west SDK checkout, portable tools
  requirements.txt        Python dependencies (west, ...)
  env/                    (generated) Python venv
  tools/                  (generated) ARM GCC, CMake, Ninja
vendor/
  mcuxsdk-manifests/      (submodule) NXP west manifest repository
  mcuxsdk/                (west-managed, gitignored) MCUXpresso SDK checkout
cmake/
  toolchain-arm-none-eabi.cmake
scripts/
  build.py                Build driver invoked by exec.bat
  elfinspect.py           ELF size/symbol analysis
  flash.py                Flash via NXP LinkServer
.vscode/                  IntelliSense, build/flash tasks, recommended extensions
src/                      The (single) firmware project
  CMakeLists.txt          Device-only MCUX SDK build (no SDK board layer)
  main.cpp                Application entry
  board/                  Pin/clock/peripheral config generated by MCUXpresso Config Tools
  utilities/              DebugConsole configuration generated by MCUXpresso Config Tools
  FRDM-MCXA266.mex        Config Tools project the board/ files are generated from
  Kconfig, prj.conf       SDK component selection
build/                    (generated) CMake/Ninja build tree
```

The project uses a *device-only* SDK build: instead of the SDK's board layer, the
pin mux, clock and peripheral setup lives in `src/board/`, generated from the
`.mex` file with [MCUXpresso Config Tools](https://www.nxp.com/design/design-center/software/development-software/mcuxpresso-software-and-tools-/mcuxpresso-config-tools-pins-clocks-and-peripherals:MCUXpresso-Config-Tools).
This keeps the template independent of NXP's board support packages and works the
same way for custom hardware.

Application code is C and C++ (C++20, `-fno-exceptions -fno-rtti`); the SDK itself
stays C and links against newlib-nano.

## VS Code integration

The repo ships a `.vscode/` setup that reuses the same toolchain and build:

- **IntelliSense** — `c_cpp_properties.json` points the C/C++ extension at
  `build/compile_commands.json` and the bundled `arm-none-eabi-gcc`, so completion
  and navigation match the real cross-compile flags. Build once to generate it.
- **Build tasks** — `Ctrl+Shift+B` runs `exec.bat build`; "Build (clean)" and "Flash"
  tasks are available via *Terminal → Run Task…*. Compiler errors land in the
  Problems panel. The Flash task depends on Build, so it always programs a
  freshly built (incremental, via Ninja) ELF — there is no way to flash stale code.
- **Status-bar buttons** — `extensions.json` recommends the
  [Task Buttons](https://marketplace.visualstudio.com/items?itemName=spencerwmiles.vscode-task-buttons)
  extension; with it installed, **Build** and **Flash** buttons appear in the
  status bar (configured in `.vscode/settings.json`). VS Code prompts to install
  the recommended extensions when the folder is opened for the first time.

## Adapting to another device

1. Set `device`, `linker_script_path` and `linkserver_device` in `config.yaml` —
   the single place for device/board specific settings. The linker script path is
   relative to the repo root, so it can point into `vendor/mcuxsdk/devices/...` or
   at a custom script committed to the repo.
2. Make sure the device family is fetched in `env/env.py` (`west update` project list).
3. Create a new `.mex` in Config Tools for your part/board and regenerate `src/board/`.
4. Adjust `src/Kconfig` / `src/prj.conf` for the drivers you need.

## Changing the SDK release

The MCUXpresso SDK version is pinned by the `vendor/mcuxsdk-manifests` submodule,
which tracks a `release/<version>` branch (currently `release/26.03.00`). The
bootstrap script consumes this manifest — **you never run `west` yourself**, it
owns the workspace in `vendor/`.

You normally only bump the release when you move to a different **MCUXpresso
Config Tools** version: the `src/board/` files it generates are tied to a
matching SDK release, so a Config Tools upgrade is the signal to align the SDK
pinned here.

To switch releases:

1. Repoint the submodule at the new release:

   ```bat
   cd vendor\mcuxsdk-manifests
   git fetch
   git checkout release/<new-version>
   cd ..\..
   git config -f .gitmodules submodule."vendor/mcuxsdk-manifests".branch release/<new-version>
   git submodule sync
   git add .gitmodules vendor\mcuxsdk-manifests
   ```

2. Force the SDK to re-sync. The bootstrap only initializes the west workspace
   when it is missing, so it will **not** pick up the new manifest on its own —
   delete the west-managed (gitignored) folders first:

   ```bat
   rmdir /s /q vendor\.west vendor\mcuxsdk
   ```

3. Re-run `exec.bat build`. With the workspace gone, the script re-runs the
   `west init` / `west update` step and fetches the SDK matching the new
   manifest.

## Roadmap

- **Multi-project layout** — multiple firmware projects side by side instead of the
  single `src/` tree.
- **Dual-core track** — build pipeline for dual-core parts (i.MX RT, MCX dual-core):
  per-core projects plus packaging of the secondary core image into the primary image.
- **i.MX realtime cores** — support the Cortex-M companion cores of i.MX application
  processors (firmware running alongside Linux, RPMsg/remoteproc deployment).
- **Zephyr support** — alternative RTOS track using the same west/CMake/Ninja
  environment next to the bare-metal MCUX SDK builds.

## License

This template itself is licensed under the [MIT License](LICENSE).

**Be aware that NXP code is licensed differently.** The MCUXpresso SDK
(submodules and the west-managed SDK checkout under `vendor/`) ships under NXP's
own license terms, *not* MIT.

This also applies to files **committed in this repo**:

- The MCUXpresso Config Tools output in `src/board/` (`pin_mux`, `clock_config`,
  `peripherals`) is generated NXP code carrying a `Copyright NXP` /
  `SPDX-License-Identifier: BSD-3-Clause` header. BSD-3-Clause is permissive but
  still requires you to retain that copyright notice and the license text — keep
  the headers intact, do not relicense those files as MIT.
- The `src/FRDM-MCXA266.mex` Config Tools project is derived from NXP's stock
  FRDM-MCXA266 board configuration, so it is likewise NXP-originated content
  (Copyright NXP). The `.mex` XML carries no SPDX header of its own — the
  `Copyright NXP` / `BSD-3-Clause` block inside it is only the template stamped
  into the generated `src/board/` files — but treat the `.mex` itself under the
  same NXP SDK terms, not MIT.

Before you distribute anything derived from this repo — your source, the
compiled binaries (`.elf`/`.bin`/`.hex`), or any other license-relevant
artifact — review the applicable NXP and third-party licenses (MIT, BSD-3-Clause
and others pulled in from the SDK) and make sure you comply with them.

This is **not** legal advice, and the author of this template accepts no
liability for how you use it.
