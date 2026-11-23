# Cuadrillapp: guía para agentes

PWA móvil para concursos de votación entre amigos. Backend Python (FastAPI + python-socketio),
frontend React 19 + Vite. La fuente de verdad del comportamiento son los specs de OpenSpec.

## Reglas de trabajo (obligatorias)

1. **Nunca push a `main`.** Trabaja en una rama (`feat/…`, `fix/…`), abre un PR y deja que CI decida.
2. **`make verify` en verde antes de cada push.** Es lo mismo que ejecuta CI (gen-check, lint, tipos,
   tests, build y e2e). Si falla, arréglalo; no lo saltes.
3. **Specs primero.** Lee `openspec/changes/*/specs` (o `openspec/specs` tras archivar). Si un cambio
   altera comportamiento, actualiza el spec en el mismo PR (skills `openspec-*`).
4. **PR corto:** qué cambia y por qué en 2-4 líneas; si es visual, adjunta una captura de Playwright
   (`page.screenshot`) en móvil.
5. **Tras el merge:** comprueba que `https://<app>.onrender.com/healthz` devuelve el SHA mergeado.
6. **Sin secretos ni datos personales** en el repo, en tests ni en logs. Nombres ficticios en ejemplos.

## Comandos

```bash
make setup      # uv sync + pnpm install + Chromium
make dev        # backend :8000 con recarga + Vite :5173
make gen        # regenera packages/protocol tras tocar apps/server/src/cuadrillapp/protocol
make verify     # todo lo de CI
```

## Mapa del código

- `apps/server/src/cuadrillapp/domain/`: reglas puras (sin I/O). `apply.py` aplica comandos sobre una
  copia de la sala; `results.py` calcula medias con `Fraction`; `projection.py` decide qué ve cada uno.
- `apps/server/src/cuadrillapp/protocol/`: modelos Pydantic de comandos/eventos. **Fuente de verdad del
  contrato**: tras cambiarlos ejecuta `make gen` y haz commit de `packages/protocol`.
- `apps/server/src/cuadrillapp/realtime/hub.py`: Socket.IO. Valida → dominio → guarda → difunde.
- `apps/web/src/copy.ts`: **todos** los textos de la UI. Botones = icono + 1-2 palabras; avisos ≤ 3
  palabras + emoji.
- `e2e/tests/`: Playwright con varios "móviles" (contextos) contra la build real.

## Invariantes que no se pueden romper

- **Atomicidad de salas:** en `hub.py` no puede haber ningún `await` entre `store.get(code)` y
  `store.put(room)`. Las consultas lentas van antes de leer la sala.
- **Anonimato:** ninguna respuesta incluye notas de otros participantes con móvil.
- **Notas en cuartos:** 0..40 en backend y protocolo; la UI muestra `7,25`.
- **Un solo worker:** las salas viven en memoria. No subas `--workers` sin el plan de escalado de
  `openspec/changes/add-live-voting/design.md` (§21).

## Despliegue y vuelta atrás

Render despliega `main` automáticamente cuando los checks pasan (`render.yaml`). Si algo se rompe:
revert por PR (`git revert <sha>`), o "Rollback" a un deploy anterior en el dashboard de Render.
Un despliegue cierra las salas abiertas: evita mergear durante una partida.
