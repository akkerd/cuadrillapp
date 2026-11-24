# Cuadrillapp 🦄🌮🐸

Contests among friends from your phone: you create a room, the others join with a code (or a QR
code), everyone picks an emoji and a name, and everyone scores everyone from 0 to 10 (in 0.25 steps)
in the categories the admin chooses. At the end, a podium with confetti.

- Installable fullscreen **PWA**, no accounts.
- **Real time** with Socket.IO; automatic reconnection when the phone locks.
- **Backend** Python 3.14 + FastAPI + python-socketio. **Frontend** React 19 + Vite + Tailwind.
- Specs and design in [`openspec/`](openspec/) (OpenSpec).
- The player-facing UI is in Spanish (`apps/web/src/copy.ts`); everything else is in English.

## Development

Requirements: [uv](https://docs.astral.sh/uv/), Node 26 and pnpm 12.

```bash
make setup    # dependencies + Chromium for e2e
make dev      # http://localhost:5173 (backend on :8000)
make verify   # the same checks as CI
```

`make` with no arguments lists every command. The working rules for agents are in
[`CLAUDE.md`](CLAUDE.md).

## Architecture

```
Phone (React PWA) ⇄ Socket.IO ⇄ Uvicorn (1 worker) ─ FastAPI (/healthz, static files)
                                                   └ python-socketio → pure domain → rooms in memory
```

- The server is the authority: the client sends commands with acks and receives room snapshots
  projected for it (nobody receives other people's scores).
- The contract lives in Pydantic models; `make gen` generates the TypeScript types in
  `packages/protocol` and CI checks that they are up to date.
- A single Docker image serves everything from the same origin.

Details and decisions: [`openspec/changes/add-live-voting/design.md`](openspec/changes/add-live-voting/design.md).

## Deployment (Render, free plan)

1. In Render: **New → Blueprint** and pick this repo. `render.yaml` creates the Docker service.
2. Render deploys `main` only when the GitHub checks pass, and does not switch traffic to the new
   version until `/healthz` responds.
3. Check the version: `curl https://<app>.onrender.com/healthz` → `{"status":"ok","version":"<sha>"}`.

The free plan puts the service to sleep after 15 minutes without traffic: the first visit takes about
a minute (the app shows a "waking up" screen).

### Rollback

- **Revert through a PR:** `git revert <sha>` on a branch, PR, green CI, merge → the previous version is deployed.
- **Immediate rollback:** Render dashboard → the service → _Events_ → _Rollback_ on a previous deploy.

A deployment closes the open rooms (they live in memory): do not merge during a game.

## Changes from your phone with Claude

1. Claude app → **Code** → `cuadrillapp` repo → describe the change.
2. The cloud session prepares itself (`.claude/settings.json` → `scripts/cloud-setup.sh`), implements
   on a branch, passes `make verify` and opens a PR.
3. Review and merge the PR from the GitHub app; Render deploys after the checks.

## Testing on real devices

Before using it at a party, check on an Android phone and an iPhone:

- [ ] Install (Android: install button; iPhone: Share → Add to Home Screen) and open from the icon:
      no browser bar.
- [ ] Nothing is hidden by the notch or the gesture bar.
- [ ] The screen stays on during voting.
- [ ] Lock the phone for 30 s and come back: you are still in the room with your scores.
