# Tasks

## 1. Monorepo scaffolding

- [x] 1.1 Create the layout (`apps/server` as a uv project with a `src/cuadrillapp` layout, `apps/web`, `packages/protocol`, `e2e`), `pnpm-workspace.yaml`, `.python-version` (3.14), `.node-version` (26), `.gitignore`; verify with `uv sync` and `pnpm install` without errors
- [x] 1.2 Configure Ruff, mypy strict (Pydantic plugin) and pytest + pytest-asyncio (`asyncio_mode = "auto"`) in `pyproject.toml` with a trivial test; configure Biome, `tsc` and Vitest in the web app with a trivial test; verify that `uv run ruff check`, `uv run mypy`, `uv run pytest` and `pnpm test` pass
- [x] 1.3 Minimal `create_app()` (FastAPI + `socketio.ASGIApp` + `Settings` with pydantic-settings) with `/healthz` → `{status, version}`; verify with an httpx test and with `uv run uvicorn cuadrillapp.main:create_app --factory` + `curl /healthz`
- [x] 1.4 `Makefile` (`setup`, `dev`, `gen`, `gen-check`, `lint`, `typecheck`, `test`, `build`, `e2e`, `verify`) and an initial `CLAUDE.md` with the rules from design.md §19; verify that `make verify` is green on a clean checkout

## 2. Protocol and constants

- [x] 2.1 Constants (30 participants, 8 categories, lengths, code alphabet without ambiguous characters, curated emoji list, category suggestions); verify with tests that the alphabet excludes 0/O/1/I/L and that emojis are not repeated
- [x] 2.2 Pydantic models for every command, the `{ok,data}|{ok,error}` ack, `ErrorCode` and the projected snapshot (`extra="forbid"`, scores as quarters 0..40); verify with tests of valid and invalid payloads (score 41, extra field, malformed code)
- [x] 2.3 `python -m cuadrillapp.protocol.export` → `packages/protocol/schema.json` + generation of `generated.ts` with `json-schema-to-typescript` (`make gen`) and `make gen-check`; verify that changing a model without regenerating makes `make gen-check` fail

## 3. Pure domain

- [x] 3.1 Helpers `scores.py` (quarters ↔ decimal) and `names.py` (normalisation with `unicodedata`: case, accents, spaces) and unique code generation; verify with tests ("  Dáni " ≡ "dani", 29 quarters = 7.25)
- [x] 3.2 Domain models (dataclasses) and `apply_command` with `deepcopy` + `match` for create, join, title, the 30-participant limit and unique names; verify with tests for the `specs/rooms` scenarios and the profile part of `specs/participants`
- [x] 3.3 Roles (locked outside the lobby), manual participants, leaving and kicking with scores discarded except in results, `SeatReleased` effect; verify with tests for `specs/participants`
- [x] 3.4 Admin permissions, grant/revoke, last admin, succession by join order with `StartGrace`/`CancelGrace` effects; verify with tests for every scenario in `specs/room-admin`
- [x] 3.5 Categories (CRUD, order, lobby only), phases and requirements to start, scores (scale, self-vote, editing, closing), proxy voting, "done" and progress; verify with tests for `specs/voting`
- [x] 3.6 `compute_results` with `Fraction` (per-category mean, final score, "no votes", ties 1,1,3), reveal (freezes), reopen and new round; verify with tests for every scenario in `specs/results`
- [x] 3.7 `project_snapshot(room, viewer_id)` (my scores; progress and proxy scores only for admins; never other people's scores) and a test that `domain/` does not import `asyncio`, `socketio` or `fastapi`; verify with tests for the "Other people's scores hidden" scenario

## 4. Server runtime

- [x] 4.1 Static files from `WEB_DIST_DIR` with SPA fallback for `/r/{code}` (excluding `/socket.io`, `/api`, `/healthz`), service-worker cache headers and the security-headers middleware; verify with httpx tests
- [x] 4.2 Socket.IO hub (rate limit → Pydantic → domain → `store.put` → per-socket projected broadcast → effects) and `MemoryRoomStore`; verify with an integration test with 3 `socketio.AsyncClient`s (create, join, everyone sees the updated list) and a test that two concurrent commands on the same room are not lost
- [x] 4.3 Presence on `connect`/`disconnect`, `room:rejoin` with a token, real `Scheduler` and `FakeScheduler`, 60 s grace and admin succession, sweep of rooms after 30 minutes in the `lifespan`; verify with integration tests using `FakeScheduler.advance()`
- [x] 4.4 Per-socket rate limit (token bucket), per-IP room creation limit and global room cap; verify with burst and invalid-data tests that leave the room unchanged

## 5. Frontend base

- [x] 5.1 Vite + React 19 + Tailwind v4 with the "party" palette tokens, self-hosted Fredoka font, `copy.ts`, base components (chunky button, card, emoji avatar, toast) and a Vite proxy to Uvicorn; verify with component tests and Playwright screenshots at 375 px
- [x] 5.2 Router (`/`, `/r/:code`), Socket.IO client typed with `@cuadrillapp/protocol`, snapshot store, reconnection with the rejoin token, "waking up" screen and lost-connection notice; verify with a store test and a manual test stopping Uvicorn
- [x] 5.3 Mapping from `ErrorCode` to short notices with emoji (not found, full, name taken…); verify with a unit test that every generated code has a text

## 6. Screens

- [x] 6.1 Home: create and join buttons, with a code field that tolerates lowercase and spaces; verify with an e2e test joining with " abc23 "
- [x] 6.2 Profile: emoji grid + 🎲 random, name, role selector, remembered profile; verify with an e2e test of a prefilled profile in a second room
- [x] 6.3 Lobby: list with crowns/status/no phone, sharing (code, link, QR, Web Share), editable title, admin panel (categories with suggestions, add manual participant, kick, role, admin) and a vote button with requirements; verify with an e2e test with an admin and 2 players
- [x] 6.4 Voting: a card per candidate with a 0.25-step slider and ± buttons, an emoji for the score, "—" when unset, autosave, progress, "done", a "vote as" selector for admins; verify with an e2e test of 7.00 → "+" → 7.25 and proxy voting
- [x] 6.5 Results: synchronised animated podium with confetti (no animation with reduced motion), category tabs with means and number of scores, reopen and new round; verify with an e2e test of the full flow and a tie check

## 7. PWA experience

- [x] 7.1 Manifest (fullscreen + standalone, portrait, maskable icons generated from the logo) and a service worker in prompt mode with an update notice that never reloads inside a room; verify with an e2e test that checks the manifest, the service-worker registration and the cache headers served by FastAPI
- [ ] 7.2 Install button (native prompt on Android, mini guide on iOS), fullscreen button when supported, Wake Lock with re-acquisition and safe areas; verify by installing on a real Android phone and a real iPhone (checklist in the README)
- [x] 7.3 Accessibility: accessible names on icon buttons, palette contrast, `prefers-reduced-motion`; verify with `@axe-core/playwright` with no serious violations on every screen

## 8. System end-to-end tests

- [x] 8.1 Playwright `webServer` that serves the build with Uvicorn; multi-device e2e of the full flow (create → 2 join → categories → vote → reveal → new round) and of a reload in the middle of voting; verify that it runs inside `make verify` in under 2 minutes
- [x] 8.2 E2E of admin succession (the admin leaves and the crown passes to the next participant) and of kicking; verify green locally and in CI

## 9. Packaging, CI/CD and deployment

- [x] 9.1 Multi-stage Dockerfile (web build with Node 26 + `python:3.14-slim` runtime with uv, unprivileged user, 1 worker) and `.dockerignore`; verify with `docker build`, `docker run` and `curl /healthz` locally
- [ ] 9.2 `ci.yml` workflow with `verify` (setup-uv + pnpm with caches, `make setup`, `make verify`, report artifact on failure) and `docker` (build + smoke test) jobs; verify with a test PR with a broken test (red) and then fixed (green)
- [ ] 9.3 Public GitHub repo with secret scanning and push protection enabled, and a main ruleset (PR + `verify` and `docker` checks, no force pushes or deletion); verify through the API that both settings are active and that a direct push to main is rejected
- [ ] 9.4 `render.yaml` (`runtime: docker`, free, `/healthz`, deploy after checks) and connecting the Blueprint (manual step for the user); check whether `autoDeployTrigger: checksPass` is available and, if not, implement the Deploy Hook fallback; verify that a green merge deploys and that `/healthz` returns the SHA
- [ ] 9.5 Test the deployment protection: a commit that breaks startup does not replace the good version; document rollback (revert through a PR and rollback in Render) in the README; verify by running both procedures once

## 10. Working with Claude from a phone

- [ ] 10.1 Complete `CLAUDE.md` (branch, `make verify`, `make gen`, atomicity rule, short PR with screenshots for visual changes, check `/healthz` after merging, OpenSpec specs as the source of truth) and the cloud environment setup script (uv + `make setup`); verify by starting a Claude cloud session that runs `make verify` green without manual steps
- [ ] 10.2 End-to-end test of the system: from the phone, ask for a small visual change, review the PR, merge from the phone and confirm the new SHA on `/healthz`; write down any friction in the README

## Workflow follow-up

- Review the deployed app with the user in a real game before archiving.
- Check the implementation against the specs with OpenSpec's `verify` workflow.
- Archive the change with `openspec archive add-live-voting` to consolidate the specs into `openspec/specs/`.
- Start `add-leagues-ranking` once this change is archived.
