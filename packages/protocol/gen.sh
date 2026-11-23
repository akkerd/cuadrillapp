#!/usr/bin/env sh
# Convierte el JSON Schema exportado por el backend en tipos TypeScript.
# Uso: sh gen.sh <schema.json> <generated.ts>
set -eu
json2ts -i "$1" -o "$2" --unreachableDefinitions --additionalProperties false \
  --bannerComment "// Generado por make gen desde apps/server. No editar a mano."
