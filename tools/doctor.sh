#!/usr/bin/env bash
# Verify that the toolchains AEGIS needs are installed, and say precisely how to
# fix each one that is not. Exits non-zero if anything required is missing.
#
# The point of this script is that a polyglot repository fails in confusing
# ways: a missing `colcon` surfaces 200 lines into a build as an unrelated
# CMake error. Failing fast with the exact remedy is worth the 40 lines.
set -uo pipefail

RED=$'\e[31m'; GRN=$'\e[32m'; YLW=$'\e[33m'; DIM=$'\e[2m'; OFF=$'\e[0m'
missing=0

check() {
    local name="$1" cmd="$2" required="$3" fix="$4"
    if command -v "$cmd" >/dev/null 2>&1; then
        local ver
        ver="$("$cmd" --version 2>&1 | head -1 | cut -c1-48)"
        printf '  %s✓%s %-18s %s%s%s\n' "$GRN" "$OFF" "$name" "$DIM" "$ver" "$OFF"
    elif [[ "$required" == "yes" ]]; then
        printf '  %s✗%s %-18s %sMISSING — %s%s\n' "$RED" "$OFF" "$name" "$RED" "$fix" "$OFF"
        missing=$((missing + 1))
    else
        printf '  %s○%s %-18s %soptional — %s%s\n' "$YLW" "$OFF" "$name" "$DIM" "$fix" "$OFF"
    fi
}

echo
echo "AEGIS toolchain check"
echo

echo "Core"
check "Python 3.10+"  python3      yes "apt install python3 python3-venv"
check "Git"           git          yes "apt install git"
check "Make"          make         yes "apt install build-essential"
echo
echo "Simulation & autonomy"
check "ROS 2"         ros2         no  "see docs/ops/setup.md — ROS 2 Jazzy"
check "colcon"        colcon       no  "pip install colcon-common-extensions"
check "Gazebo"        gz           no  "see docs/ops/setup.md — Gazebo Harmonic"
echo
echo "Backend & web"
check "Docker"        docker       no  "see docs/ops/setup.md — Docker Engine"
check "Node 20+"      node         no  "see docs/ops/setup.md — via nvm"
check "pnpm"          pnpm         no  "corepack enable && corepack prepare pnpm@latest --activate"
echo
echo "Firmware"
check "PlatformIO"    pio          no  "pip install platformio"
echo

if (( missing > 0 )); then
    printf '%s%d required tool(s) missing.%s See docs/ops/setup.md\n\n' "$RED" "$missing" "$OFF"
    exit 1
fi
printf '%sCore toolchain present.%s Optional tools are only needed for the\n' "$GRN" "$OFF"
printf 'subsystems they serve — see docs/ops/setup.md.\n\n'
