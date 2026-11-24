#!/usr/bin/env bash
# Prepare a clean machine (e.g. a Claude Code cloud session). Needs no secrets.
set -euo pipefail
cd "$(dirname "$0")/.."
command -v uv >/dev/null || python3 -m pip install --user --quiet uv
export PATH="$HOME/.local/bin:$PATH"
command -v pnpm >/dev/null || npm install -g pnpm@12.21.0
make setup PLAYWRIGHT_DEPS=--with-deps
