#!/usr/bin/env bash
# Run every test suite whose toolchain is present, and say clearly which ones
# were skipped.
#
# The "say clearly" part matters. A test runner that silently skips two of four
# suites and prints "PASSED" is actively misleading — the whole point of running
# tests is to know what is verified, and a skipped suite verifies nothing.
set -uo pipefail
cd "$(dirname "$0")/.."

BOLD=$'\e[1m'; RED=$'\e[31m'; GRN=$'\e[32m'; YLW=$'\e[33m'; DIM=$'\e[2m'; OFF=$'\e[0m'
failed=0
ran=()
skipped=()

section() { printf '\n%s%s%s\n' "$BOLD" "$1" "$OFF"; }
skip()    { printf '  %s- skipped: %s%s\n' "$DIM" "$2" "$OFF"; skipped+=("$1"); }
run() {
    local name="$1"; shift
    if "$@"; then
        ran+=("$name")
    else
        printf '  %s✗ %s failed%s\n' "$RED" "$name" "$OFF"
        failed=$((failed + 1))
        ran+=("$name (FAILED)")
    fi
}

[[ -d .venv ]] && source .venv/bin/activate

section "Python — shared library"
if command -v pytest >/dev/null 2>&1; then
    # SITL and GPU suites are excluded here and run by their own targets; a
    # missing SITL is not a test failure.
    run "python" pytest tests/ -q -m "not sitl and not gpu and not integration"
else
    skip "python" "pytest missing — run 'make setup-python'"
fi

section "ROS 2 — autonomy"
if command -v colcon >/dev/null 2>&1 && \
   [[ -n "$(find autonomy/src -name 'package.xml' -print -quit 2>/dev/null)" ]]; then
    run "autonomy" bash -c "cd autonomy && colcon test && colcon test-result --verbose"
else
    skip "autonomy" "no ROS 2, or autonomy/src has no packages yet"
fi

section "Web"
if [[ -f web/package.json ]] && command -v pnpm >/dev/null 2>&1; then
    run "web" bash -c "cd web && pnpm test --run"
else
    skip "web" "no web/package.json yet, or pnpm missing"
fi

section "Firmware"
if command -v pio >/dev/null 2>&1 && [[ -f firmware/platformio.ini ]]; then
    run "firmware" bash -c "cd firmware && pio test -e native"
else
    skip "firmware" "no firmware/platformio.ini yet, or PlatformIO missing"
fi

printf '\n%s──────────────────────────────────────%s\n' "$DIM" "$OFF"
printf 'Ran:     %s\n' "${ran[*]:-none}"
if ((${#skipped[@]} > 0)); then
    printf '%sSkipped: %s%s\n' "$YLW" "${skipped[*]}" "$OFF"
    printf '%sThose suites verified nothing. See docs/ops/setup.md.%s\n' "$DIM" "$OFF"
fi

if ((failed > 0)); then
    printf '\n%s%d suite(s) failed.%s\n\n' "$RED" "$failed" "$OFF"
    exit 1
fi
printf '\n%sAll suites that could run, passed.%s\n\n' "$GRN" "$OFF"
