# Cuadrillapp: guide for agents

Mobile PWA for voting contests among friends. Python backend (FastAPI + python-socketio), React 19 +
Vite frontend. The OpenSpec specs are the source of truth for behaviour.

## Working rules (mandatory)

1. **Never push to `main`.** Work on a branch (`feat/…`, `fix/…`), open a PR and let CI decide.
2. **`make verify` green before every push.** It is exactly what CI runs (gen-check, lint, types,
   tests, build and e2e). If it fails, fix it; never skip it.
3. **Specs first.** Read `openspec/changes/*/specs` (or `openspec/specs` once archived). If a change
   alters behaviour, update the spec in the same PR (`openspec-*` skills).
4. **Short PR:** what changes and why in 2-4 lines; for visual changes attach a Playwright screenshot
   (`page.screenshot`) at phone size.
5. **After merging:** check that `https://<app>.onrender.com/healthz` returns the merged SHA.
6. **No secrets or personal data** in the repo, tests or logs. Use fictional names in examples.
7. **English only.** Code, comments, docs, specs, tests, commits and PR texts are written in English.
   The only exception is player-facing UI copy, which lives in `apps/web/src/copy.ts`.

## Commands

```bash
make setup      # uv sync + pnpm install + Chromium
make dev        # backend on :8000 with reload + Vite on :5173
make gen        # regenerate packages/protocol after touching apps/server/src/cuadrillapp/protocol
make verify     # everything CI runs
```

## Code map

- `apps/server/src/cuadrillapp/domain/`: pure rules (no I/O). `apply.py` applies commands to a copy
  of the room; `results.py` computes means with `Fraction`; `projection.py` decides what each viewer sees.
- `apps/server/src/cuadrillapp/protocol/`: Pydantic models for commands and events. **Source of truth
  for the contract**: after changing them run `make gen` and commit `packages/protocol`.
- `apps/server/src/cuadrillapp/realtime/hub.py`: Socket.IO. Validate → domain → store → broadcast.
- `apps/web/src/copy.ts`: **every** UI string. Buttons = icon + 1-2 words; notices ≤ 3 words + emoji.
- `e2e/tests/`: Playwright with several "phones" (browser contexts) against the real build.

## Invariants that must not break

- **Room atomicity:** in `hub.py` there must be no `await` between `store.get(code)` and
  `store.put(room)`. Slow queries go before reading the room.
- **Anonymity:** no response includes scores given by other participants with a phone.
- **Scores in quarters:** 0..40 in the backend and the protocol; the UI shows `7,25` (Spanish locale).
- **A single worker:** rooms live in memory. Do not raise `--workers` without the scaling plan in
  `openspec/changes/add-live-voting/design.md` (§21).

## Deployment and rollback

Render deploys `main` automatically when the checks pass (`render.yaml`). If something breaks:
revert through a PR (`git revert <sha>`), or "Rollback" to a previous deploy in the Render dashboard.
A deployment closes the open rooms: avoid merging during a game.
