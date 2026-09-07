#!/usr/bin/env bash
# Lint every language in the tree, skipping the ones whose toolchain is absent.
#
# Skipping rather than failing is deliberate: this repository spans four
# toolchains and almost nobody has all four installed. A contributor working on
# the ESP32 firmware should not be blocked by a missing ROS 2, and a lint script
# that fails for that reason gets bypassed with --no-verify, which is worse than
# one that is honest about what it did and did not check.
set -uo pipefail
cd "$(dirname "$0")/.."

BOLD=$'\e[1m'; RED=$'\e[31m'; GRN=$'\e[32m'; YLW=$'\e[33m'; DIM=$'\e[2m'; OFF=$'\e[0m'
failed=0
skipped=()

section() { printf '\n%s%s%s\n' "$BOLD" "$1" "$OFF"; }
skip()    { printf '  %s- %s (skipped: %s)%s\n' "$DIM" "$1" "$2" "$OFF"; skipped+=("$1"); }
run() {
    local name="$1"; shift
    if "$@"; then
        printf '  %s✓%s %s\n' "$GRN" "$OFF" "$name"
    else
        printf '  %s✗%s %s\n' "$RED" "$OFF" "$name"
        failed=$((failed + 1))
    fi
}

[[ -d .venv ]] && source .venv/bin/activate

section "Python"
if command -v ruff >/dev/null 2>&1; then
    run "ruff check" ruff check aegis/ tests/
else
    skip "ruff" "pip install -e '.[dev]'"
fi
if command -v mypy >/dev/null 2>&1; then
    run "mypy" mypy aegis/
else
    skip "mypy" "pip install -e '.[dev]'"
fi

section "Shell"
if command -v shellcheck >/dev/null 2>&1; then
    run "shellcheck" shellcheck tools/*.sh
else
    skip "shellcheck" "apt install shellcheck"
fi

section "ROS 2 workspace"
if command -v colcon >/dev/null 2>&1 && [[ -d autonomy/src ]] && \
   [[ -n "$(find autonomy/src -name 'package.xml' -print -quit 2>/dev/null)" ]]; then
    run "colcon lint" bash -c "cd autonomy && colcon test --packages-select-regex 'aegis_.*' --ctest-args -R lint"
else
    skip "colcon" "no ROS 2, or autonomy/src has no packages yet"
fi

section "Web"
if [[ -f web/package.json ]] && command -v pnpm >/dev/null 2>&1; then
    run "eslint" bash -c "cd web && pnpm lint"
else
    skip "eslint" "no web/package.json yet, or pnpm missing"
fi

section "Licences"
if [[ -f tools/check_licences.py ]]; then
    run "licence policy" python tools/check_licences.py
else
    skip "licence check" "tools/check_licences.py not written yet (ADR-0004)"
fi

printf '\n'
if ((${#skipped[@]} > 0)); then
    printf '%sSkipped: %s%s\n' "$YLW" "${skipped[*]}" "$OFF"
fi
if ((failed > 0)); then
    printf '%s%d check(s) failed.%s\n\n' "$RED" "$failed" "$OFF"
    exit 1
fi
printf '%sAll available checks passed.%s\n\n' "$GRN" "$OFF"
