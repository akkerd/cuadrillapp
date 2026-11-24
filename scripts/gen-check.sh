#!/usr/bin/env bash
# Fail if packages/protocol does not match the backend's Pydantic models.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

(cd "$root/apps/server" && uv run --quiet python -m cuadrillapp.protocol.export "$tmp")
(cd "$root/packages/protocol" && pnpm exec sh gen.sh "$tmp/schema.json" "$tmp/src/generated.ts")

for file in schema.json src/events.ts src/constants.ts src/generated.ts; do
  if ! diff -q "$root/packages/protocol/$file" "$tmp/$file" >/dev/null; then
    echo "✗ packages/protocol/$file is out of date: run 'make gen' and commit." >&2
    exit 1
  fi
done
echo "✓ Protocol contract is up to date"
