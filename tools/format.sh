#!/usr/bin/env bash
# Auto-format every language whose toolchain is present.
#
# Unlike lint.sh this mutates files, so it is never run in CI — CI runs
# `ruff format --check` via lint instead. Formatting in CI produces commits
# nobody reviewed.
set -uo pipefail
cd "$(dirname "$0")/.."

BOLD=$'\e[1m'; GRN=$'\e[32m'; DIM=$'\e[2m'; OFF=$'\e[0m'

section() { printf '\n%s%s%s\n' "$BOLD" "$1" "$OFF"; }
skip()    { printf '  %s- %s (skipped: %s)%s\n' "$DIM" "$1" "$2" "$OFF"; }
did()     { printf '  %s✓%s %s\n' "$GRN" "$OFF" "$1"; }

[[ -d .venv ]] && source .venv/bin/activate

section "Python"
if command -v ruff >/dev/null 2>&1; then
    ruff format aegis/ tests/ -q && did "ruff format"
    # --fix applies the safe autofixes: import sorting, __all__ ordering,
    # comprehension rewrites. Unsafe fixes are deliberately not applied.
    ruff check aegis/ tests/ --fix -q && did "ruff check --fix"
else
    skip "ruff" "pip install -e '.[dev]'"
fi

section "Web"
if [[ -f web/package.json ]] && command -v pnpm >/dev/null 2>&1; then
    (cd web && pnpm format) && did "prettier"
else
    skip "prettier" "no web/package.json yet, or pnpm missing"
fi

section "Firmware"
if command -v clang-format >/dev/null 2>&1 && \
   [[ -n "$(find firmware -name '*.cpp' -o -name '*.h' -print -quit 2>/dev/null)" ]]; then
    find firmware -name '*.cpp' -o -name '*.h' | xargs clang-format -i && did "clang-format"
else
    skip "clang-format" "no firmware sources yet, or clang-format missing"
fi

printf '\n'
