# Development environment setup

## Evidence status: 2026-09-08

These are setup instructions, not proof that this machine is configured. This
session did not install toolchains, run `make doctor`, or requalify the documented
Jetson/JetPack/Ubuntu/ROS compatibility matrix. Earlier machine-state statements
are historical. Confirm exact supported versions before a future installation;
do not infer compatibility or working targets from a planned stack alone.
See the [handoff](../HANDOFF-2026-09-08.md) for the next bounded task and open gates.


Target platform is **Ubuntu 24.04 LTS**. That is not incidental — it is forced by
a constraint chain worth understanding before you substitute anything:

> ROS 2 **Jazzy Jalisco** is Tier-1 on Ubuntu 24.04. The newer LTS, Lyrical Luth
> (May 2026), is Tier-1 on Ubuntu 26.04 — for which **no JetPack exists**, because
> JetPack 7 is built on 24.04. Since the companion computer is a Jetson
> ([ADR-0005](../adr/0005-ardupilot-over-px4.md)), Jazzy is the only ROS 2 LTS that
> fits the deployment target, and the dev machine matches the target.

Run `make doctor` at any point. It reports what is present, what is missing, and
the exact remedy for each — including which subsystems you can work on without a
given tool.

Nothing here is needed all at once. The table says what each toolchain unlocks.

| Toolchain | Needed for | Skip it if |
| --- | --- | --- |
| Python 3.10+ | Everything. The shared library and its tests. | Never |
| ROS 2 Jazzy + colcon | `autonomy/` — flight nodes, sortie state machine | You are working on perception, backend or web |
| Gazebo Harmonic + ArduPilot SITL | `sim/` — flying anything | Same |
| CUDA + PyTorch | `perception/` — training and export | You are only running inference or writing services |
| Docker | `services/`, `infra/` — the edge and cloud stack | You are working on the library or firmware |
| Node 20+ / pnpm | `web/` — the ops dashboard | Anything else |
| PlatformIO | `firmware/` — ESP32 nodes | Anything else |

---

## 1. Core (required)

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip build-essential git cmake

cd /path/to/aegis
make setup-python     # creates .venv and installs the project with dev extras
make test             # should be green
```

The virtualenv lives at `.venv/` and is gitignored. Every `make` target that runs
Python activates it itself, so you do not need to source it manually.

---

## 2. ROS 2 Jazzy + colcon

```bash
sudo apt install -y software-properties-common curl
sudo add-apt-repository universe

sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
  -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] \
http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" \
  | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

sudo apt update
sudo apt install -y ros-jazzy-desktop ros-dev-tools ros-jazzy-mavros ros-jazzy-mavros-extras
```

MAVROS needs the GeographicLib geoid datasets, and this is easy to miss — without
them MAVROS will not convert between AMSL and ellipsoidal height, which is exactly
the datum confusion `aegis/domain/geo.py` exists to prevent:

```bash
sudo /opt/ros/jazzy/lib/mavros/install_geographiclib_datasets.sh
```

Then, per shell (or in `~/.bashrc`):

```bash
source /opt/ros/jazzy/setup.bash
```

Build the workspace with `make autonomy-build`.

> **Note.** ArduPilot's native ROS 2 bridge (`AP_DDS`) documents support for ROS 2
> **Humble only**, and on STM32 requires an H7-class board. We therefore bridge
> with MAVROS rather than AP_DDS. See [ADR-0005](../adr/0005-ardupilot-over-px4.md).

---

## 3. Gazebo Harmonic + ArduPilot SITL

Gazebo **Harmonic** is the LTS (supported to May 2029). Do not start on Ionic —
it reaches EOL in December 2026.

```bash
sudo curl -sSL https://packages.osrfoundation.org/gazebo.gpg \
  -o /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] \
http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" \
  | sudo tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null

sudo apt update
sudo apt install -y gz-harmonic
```

ArduPilot SITL:

```bash
git clone --recurse-submodules https://github.com/ArduPilot/ardupilot.git ~/ardupilot
cd ~/ardupilot
Tools/environment_install/install-prereqs-ubuntu.sh -y
. ~/.profile
./waf configure --board sitl && ./waf copter
```

And the Gazebo bridge plugin:

```bash
git clone https://github.com/ArduPilot/ardupilot_gazebo ~/ardupilot_gazebo
cd ~/ardupilot_gazebo && mkdir -p build && cd build
cmake .. -DCMAKE_BUILD_TYPE=RelWithDebInfo && make -j$(nproc)
```

Add to your shell profile:

```bash
export GZ_SIM_SYSTEM_PLUGIN_PATH=$HOME/ardupilot_gazebo/build:$GZ_SIM_SYSTEM_PLUGIN_PATH
export GZ_SIM_RESOURCE_PATH=$HOME/ardupilot_gazebo/models:$HOME/ardupilot_gazebo/worlds:$GZ_SIM_RESOURCE_PATH
```

Launch with `make sim`, or `make sim-headless` for CI and batch runs.

> **Do not** reach for AirSim. Microsoft AirSim shut down in 2022, Project AirSim
> at the end of 2023, and the community Colosseum fork was archived read-only on
> 2026-07-11. None can be a project dependency. Photorealism, if we need it later,
> comes from Isaac Sim 5.1.0 + Pegasus Simulator v5.1.0 — pinned together, because
> Pegasus has no release for Isaac 6.0.x. Isaac Sim 6.0 also needs an RTX 4080 with
> 16 GB VRAM minimum, which the current dev machine (RTX 4060 Mobile, 8 GB) does
> not meet. Gazebo Harmonic is the working loop.

### ArduPilot parameter caveat

Copter 4.7 converted RTL parameters to SI units and renamed them
(`RTL_ALT` → `RTL_ALT_M`). Parameter files written for 4.6 or earlier **will not
apply cleanly**. Rally point altitudes also override `RTL_ALT_M`, so the two are
configured together or not at all.

---

## 4. GPU / PyTorch (for training only)

Verify the driver first:

```bash
nvidia-smi
```

Then install PyTorch into the project venv, matching your CUDA version — check
<https://pytorch.org/get-started/locally/> for the current index URL rather than
copying one from here, since it changes:

```bash
. .venv/bin/activate
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
python -c "import torch; print(torch.__version__, torch.cuda.is_available())"
```

Then `pip install -e '.[train]'`.

> **Licence guard.** Do not `pip install ultralytics`, in this venv or any other,
> including for a quick comparison. Every Ultralytics generation is AGPL-3.0 and
> an import in a notebook that produces a published benchmark number is still a
> derivative work. See [ADR-0004](../adr/0004-rf-detr-over-ultralytics-yolo.md).

---

## 5. Docker

```bash
sudo apt install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] \
https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER   # log out and back in
```

Bring the stack up with `make up`, down with `make down`, logs with `make logs`.

---

## 6. Node and pnpm

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/master/install.sh | bash
# reopen the shell
nvm install 20 && nvm use 20
corepack enable && corepack prepare pnpm@latest --activate
```

Then `make setup-web` and `make web`.

---

## 7. PlatformIO (ESP32)

```bash
. .venv/bin/activate
pip install platformio
```

Serial access without `sudo`:

```bash
sudo usermod -aG dialout $USER   # log out and back in
```

Build with `make firmware`.

---

## Troubleshooting

**`make test` fails with `Unknown config option: asyncio_mode`.**
`pytest-asyncio` is missing. `pip install -e '.[dev]'` inside the venv.

**`colcon build` cannot find ROS packages.**
You have not sourced ROS in this shell. `source /opt/ros/jazzy/setup.bash`.

**Gazebo starts but the aircraft does not appear.**
`GZ_SIM_SYSTEM_PLUGIN_PATH` and `GZ_SIM_RESOURCE_PATH` are not exported in the
shell that launched it. They must be set in the same shell, not just in
`~/.bashrc` of a different terminal.

**`torch.cuda.is_available()` is `False`.**
Either the driver is older than the CUDA build you installed, or you installed
the CPU wheel. Check `nvidia-smi` reports a CUDA version at least as new as the
wheel's, and reinstall from the matching index URL.

**Permission denied on `/dev/ttyUSB0`.**
You are not in the `dialout` group, or you have not logged out since being added.
