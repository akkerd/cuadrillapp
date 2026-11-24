# Design

## Context

New project (empty repo). Motivation and scope are in `proposal.md`; behaviour is in `specs/`. Constraints that shape the design:

- Real use: groups of 3-30 friends in the same room, each with a phone, sessions of 10-60 minutes. Minimal load.
- Test project without a budget: free hosting.
- **Python** backend (the user's choice: something simple and scalable "like Flask"); React frontend.
- The code will mostly be changed by Claude, often from cloud sessions started from a phone with the laptop switched off: everything must install, test and verify with a single command, without Docker and without secrets.
- This change persists nothing; `add-leagues-ranking` will add a database and login. The design leaves room for it (same origin for cookies, pure domain, storage interfaces) without implementing it.

## Goals / Non-Goals

**Goals:**
- A single deployable artifact (Docker image) that serves the PWA, the health endpoint and the real-time channel from the same origin.
- Business rules in pure Python functions with fast tests; network, clock and timers in a thin layer around them.
- A client-server contract with a single source of truth (Pydantic) and generated TypeScript types.
- A defined horizontal scaling path (swappable interfaces), even though a single instance runs today.
- A pipeline where merging to main is the only way to deploy, and only with green checks.

**Non-Goals:**
- Implementing horizontal scaling or rooms that survive restarts now.
- Server-side rendering (SSR) or SEO.
- Optimising for old desktop browsers (priority: recent Chrome on Android and Safari on iOS).

## Architecture

```
 Phone (PWA)                                   Render (free plan, 1 instance, Docker)
┌──────────────────────────┐   HTTPS          ┌────────────────────────────────────────────┐
│ React 19 + Vite          │ ───────────────▶ │ Uvicorn (1 worker) → socketio.ASGIApp      │
│  screens ← store         │   GET /, /r/:c   │  ├─ FastAPI                                │
│  (latest snapshot)       │   GET /healthz   │  │   ├─ /healthz → {status, version: SHA}  │
│        ▲         │       │                  │  │   └─ PWA static files + SPA fallback    │
│ snapshot│      command    │   WebSocket      │  └─ python-socketio AsyncServer            │
│        │         ▼       │ ◀──────────────▶ │      ├─ parse: rate limit + Pydantic       │
│ socket.io-client          │  (poll fallback) │      ├─ apply_command() ── pure domain     │
│ Service Worker (shell)   │                  │      ├─ RoomStore (MemoryRoomStore)        │
└──────────────────────────┘                  │      ├─ Scheduler (asyncio)                │
                                              │      └─ project_snapshot() per viewer      │
                                              └────────────────────────────────────────────┘
 GitHub: PR → Actions (make verify + docker build) → protected main → Render deploys after checks
```

Repository layout:

```
cuadrillapp/
├─ apps/
│  ├─ server/                     uv project (Python 3.14)
│  │  ├─ pyproject.toml           deps + Ruff, mypy and pytest config
│  │  ├─ uv.lock
│  │  ├─ src/cuadrillapp/
│  │  │  ├─ main.py               build_app()/create_app(): FastAPI + Socket.IO → ASGI app
│  │  │  ├─ settings.py           Settings (pydantic-settings)
│  │  │  ├─ constants.py          limits and catalogs (exported to the frontend)
│  │  │  ├─ domain/               PURE: models.py, apply.py, effects.py, results.py,
│  │  │  │                        scores.py, names.py, codes.py, projection.py, errors.py
│  │  │  ├─ protocol/             Pydantic commands, acks and snapshot; registry.py, export.py
│  │  │  ├─ realtime/             hub.py (Socket.IO), ratelimit.py, scheduler.py
│  │  │  ├─ store/                base.py (RoomStore Protocol), memory.py
│  │  │  └─ http/                 health.py, static.py, security.py
│  │  └─ tests/                   unit/ (domain), integration/ (HTTP and sockets)
│  └─ web/                        React PWA (Vite)
├─ packages/protocol/             generated TS types (do not edit by hand)
├─ e2e/                           Playwright (several devices)
├─ openspec/                      specs and changes
├─ Dockerfile, render.yaml, Makefile, CLAUDE.md
├─ pnpm-workspace.yaml            apps/web, packages/protocol, e2e
└─ .github/workflows/ci.yml
```

## Decisions

### 1. FastAPI instead of Flask
FastAPI keeps Flask's simplicity (one app, routes with decorators, little code), but it is **ASGI and asynchronous out of the box**, which is what a real-time app needs: thousands of open WebSockets in a single process without threads or monkey-patching. It also brings built-in validation with Pydantic and automatic OpenAPI (useful to generate frontend types in change 2).
- *Alternative:* Flask + Flask-SocketIO. It works, but its async modes rely on eventlet (deprecated) or on gevent with monkey-patching, which complicates async libraries (database, OAuth) and debugging. The threaded mode scales worse with long-lived connections.
- *Alternative:* Quart (async Flask). Same API as Flask, but a much smaller ecosystem and less documentation.
- *Alternative:* Django + Channels. Too heavy for an app without complex business models in this change.

### 2. Real time with python-socketio in ASGI mode
`socketio.AsyncServer(async_mode="asgi")` wraps FastAPI into a single ASGI app:

```python
# main.py
def build_app(settings: Settings | None = None, *, scheduler=None, clock=None) -> AppBundle:
    settings = settings or Settings()
    hub = RealtimeHub(settings, MemoryRoomStore(), scheduler or AsyncioScheduler(), clock or time.monotonic)
    api = FastAPI(lifespan=lifespan, docs_url=None if settings.is_production else "/api/docs")
    api.add_middleware(SecurityHeadersMiddleware)
    api.include_router(health_router(settings))
    api.mount("/", SpaStaticFiles(directory=settings.web_dist_dir))   # last: SPA fallback
    asgi = socketio.ASGIApp(hub.sio, other_asgi_app=api, socketio_path="socket.io")
    return AppBundle(asgi=asgi, api=api, hub=hub)
```

The client stays `socket.io-client`: acks, heartbeats, reconnection with backoff and long-polling fallback on mobile networks that drop WebSockets, without reimplementing them.
- *Alternative:* FastAPI's native WebSockets. Rejected: acks, reconnection, heartbeats and rooms would have to be written by hand, which is exactly the delicate part on mobile.
- It runs with `uvicorn cuadrillapp.main:create_app --factory` and **1 worker**: room state lives in the process (see decision 7 and "Scaling path").

### 3. A single service on the same origin
FastAPI serves the web's static build (`StaticFiles` for `/assets` and service-worker files) and falls back to `index.html` for SPA routes (`/r/{code}`), excluding `/socket.io`, `/api` and `/healthz`. No CORS, no cross-domain requests, and first-party cookies ready for change 2's login. In development, Vite runs on `:5173` and proxies `/socket.io`, `/api` and `/healthz` to Uvicorn on `:8000`.

### 4. Authoritative server: commands with acks and projected snapshots
- **Client → server:** one event per command (`room:create`, `room:peek`, `room:join`, `room:rejoin`, `room:leave`, `room:title`, `participant:update`, `participant:kick`, `admin:set`, `manual:add`, `category:add`, `category:update`, `category:delete`, `category:move`, `voting:start`, `voting:reveal`, `voting:reopen`, `round:new`, `score:set`, `voter:done`). Every in-room command goes through one path in `realtime/hub.py`:

```python
async def _dispatch(self, model: type[Command], sid: str, data: object) -> AckPayload:
    cmd = self._parse(sid, model, data)            # rate limit + Pydantic validation
    if isinstance(cmd, dict):
        return cmd                                  # {"ok": false, "error": ...}
    session = await self.sio.get_session(sid)       # {room, pid}
    return await self.apply(session["room"], session["pid"], cmd)

async def apply(self, code: str, participant_id: str, cmd) -> AckPayload:
    room = self.store.get(code)
    if room is None:
        return ack_error("ROOM_NOT_FOUND")
    outcome = apply_command(room, participant_id, cmd, self.clock())
    if isinstance(outcome, DomainError):
        return ack_error(outcome.code)
    self.store.put(outcome.room)                   # ← no await between get and put
    await self._run_effects(code, outcome.effects) # timers, kicked notices…
    await self.broadcast(code)
    return ack_ok(outcome.data)
```

- **Atomicity:** with a single event loop and no `await` between reading and storing the room, two commands never interleave on the same room. `CLAUDE.md` states this rule and a concurrency test protects it.
- **Server → client:** after every mutation, `broadcast` emits `room:state` **to each socket separately** with `project_snapshot(room, viewer_id)`: public room data + my scores + (for admins) per-voter progress and the scores of manual participants. Other people's scores never leave the server (anonymity spec). Each snapshot carries a `version`; clients drop older versions, so concurrent emits cannot leave a device with stale state.
- With ≤30 participants × ≤8 categories a snapshot is a few KB; diffs are not worth it.
- The client keeps the latest snapshot in a store (Zustand) and the UI is a function of it, with local optimistic updates on the scoring screen.

### 5. Pure domain in Python
- `domain/models.py`: `@dataclass(slots=True)` for `Room`, `Participant`, `Category`; scores are a dict `(voter_id, candidate_id, category_id) → quarters`; frozen `Results`. Value types use `Literal` (not stdlib `Enum`) so they serialise cleanly.
- `domain/apply.py`: `apply_command(room, actor_id, cmd, now) -> Applied | DomainError`. It works on `copy.deepcopy(room)` (rooms are tiny): if a rule fails halfway, the copy is discarded and the original room is untouched. It dispatches with `match cmd:` on the command type.
- `Applied` carries the new room, the response data and declarative **effects** (`StartGrace(pid)`, `CancelGrace(pid)`, `SeatReleased(pid, kicked)`) that the realtime layer executes. The domain stays free of I/O and timers.
- `domain/results.py`: `compute_results(room) -> Results` with `fractions.Fraction` for exact means; rankings and ties compare fractions and are only rounded to 2 decimals when serialised. Change 2 reuses it.
- The clock is injected (`now: float`); nothing in `domain/` imports `asyncio`, `socketio` or `fastapi` (an import test checks it).

### 6. Typed contract from a single source (Pydantic → TypeScript)
- `protocol/` defines with Pydantic v2 every command (`ScoreSet(candidate_id, category_id, quarters: int 0..40 | None, as_participant_id)`, …), the ack format (`{"ok": true, "data": …} | {"ok": false, "error": ErrorCode}`), the error codes and the projected snapshot, with `extra="forbid"`, `strict=True` and camelCase JSON.
- `python -m cuadrillapp.protocol.export` writes `packages/protocol/schema.json` (JSON Schema of every model), `src/events.ts` (typed event map, error codes, literals) and `src/constants.ts` (limits, code alphabet, emojis, category suggestions); `json-schema-to-typescript` generates `packages/protocol/src/generated.ts`. The web only imports from `@cuadrillapp/protocol`.
- `make gen` regenerates; `make gen-check` (part of `make verify` and CI) fails if the generated files do not match the models → client and server cannot drift apart without CI noticing.
- *Alternative:* hand-written duplicate TS types. Rejected: silent drift between languages.

### 7. In-memory room state behind an interface
- `store/base.py`: `class RoomStore(Protocol)` with `get`, `put`, `delete`, `exists`, `codes`, `count`. `store/memory.py`: `MemoryRoomStore` with a `dict[str, Room]`.
- A sweep every 60 s, run as an `asyncio` task started in FastAPI's `lifespan`, deletes rooms with 30 minutes without connections. Global cap on active rooms (300) and on room creation per IP (10/min).
- *Accepted consequence:* a restart or deployment closes every active room (spec "Server restart"); the client receives `ROOM_NOT_FOUND` on `room:rejoin` and shows "room closed".

### 8. Seat identity, presence and timers
- On joining, the server returns `participantId` and a `rejoin token` (`secrets.token_urlsafe(16)`) that the client stores in `localStorage` per room code. `room:rejoin {code, token}` recovers the seat; kicking invalidates the token. The server keeps `{room, pid}` in the Socket.IO session.
- Socket.IO `connect`/`disconnect` update presence (`connected` ↔ `disconnected`). `joined_seq` (a per-room counter) defines join order.
- `realtime/scheduler.py`: `class Scheduler(Protocol)` with `call_later(delay, key, callback)`, `cancel(key)` and `cancel_prefix(prefix)`. The real implementation uses `asyncio.get_running_loop().call_later`; tests use `FakeScheduler` with `advance(seconds)` to check the 60 s grace period and succession without waiting.

### 9. Scores as integer quarters
A score is an integer 0..40 (quarter points) everywhere in the backend and the protocol. The web converts it for display with `Intl.NumberFormat` in the UI language. This removes floating-point errors and makes validation trivial (`0 <= quarters <= 40`).

### 10. Configuration
`settings.py` with `pydantic-settings`: `ENV` (`development|test|production`), `WEB_DIST_DIR`, `RENDER_GIT_COMMIT` (version for `/healthz`), `CORS_ORIGINS`, and the rate-limit, room-cap and timer settings. A single `Settings` object is injected into `build_app()`; tests build apps with their own settings.

### 11. Python tooling
- **uv**: manages Python 3.14 (`.python-version`), the virtualenv, dependencies and `uv.lock`. Everything runs through `uv run …`.
- **Ruff** (lint + format), **mypy --strict** with the Pydantic plugin, **pytest** + **pytest-asyncio** (`asyncio_mode = "auto"`), **httpx** for HTTP tests.
- Minimal runtime dependencies: `fastapi`, `uvicorn[standard]`, `python-socketio`, `pydantic`, `pydantic-settings`.
- Python 3.14 rather than 3.15 because of dependency wheel maturity; upgrading means changing `.python-version` and the base image.

### 12. Frontend
- React 19 + Vite + React Router (routes `/`, `/crear`, `/r/:code`); screens: Home, Profile, Lobby, Voting, Results. Inside `/r/:code` the screen is derived from the snapshot's phase.
- Tailwind CSS v4 with tokens in CSS variables. Our own "party" palette: grape gradient background (#5B2EE5 → #8F3CF7), yellow #FFD23F, pink #FF5FA2, turquoise #22C9B7, orange #FF8A3D, ink #1E1338. Rounded typeface (Fredoka, self-hosted). Chunky buttons with a hard 3D-style bottom shadow and very rounded cards. Inspired by the feel of party games, without copying assets or the look of any specific game.
- Motion for spring animations (respecting `prefers-reduced-motion`), `canvas-confetti` on the podium, `lucide-react` for icons, `qrcode` for the QR code (generated on the client). QR and confetti are loaded lazily.
- All player-facing text lives in `apps/web/src/copy.ts`. The emoji list and category suggestions come from `@cuadrillapp/protocol` (defined once in Python).
- Biome (lint + format), `tsc --noEmit`, Vitest + Testing Library.

### 13. PWA
`vite-plugin-pwa` (Workbox `generateSW`): precaches the shell and fonts; no data caching. Manifest with `display: "fullscreen"`, `display_override: ["fullscreen", "standalone"]`, `orientation: "portrait"`, 192/512 icons plus a maskable one, and `theme_color`. Registration in `prompt` mode: the update notice only reloads when the user taps it. iOS falls back to `standalone` + `viewport-fit=cover` + `env(safe-area-inset-*)`. Wake Lock API while in a room, re-acquired on `visibilitychange`. Fullscreen button only when `document.fullscreenEnabled`. FastAPI serves `sw.js` and `manifest.webmanifest` with `Cache-Control: no-cache` and hashed assets with long-lived caching.

### 14. Testing strategy
1. **Unit (pytest):** domain and results; every scenario in the `rooms`, `participants`, `room-admin`, `voting` and `results` specs has a test named after it.
2. **Integration (pytest-asyncio):** a fixture starts `uvicorn.Server` with `build_app(test_settings)` on a free port inside the test's event loop and connects several `socketio.AsyncClient`s acting as phones (joining, anonymous projection, reconnection, rate limiting, concurrency). Timers use `FakeScheduler`. HTTP uses `httpx.AsyncClient(transport=ASGITransport(app))`.
3. **Web (Vitest):** store, error mapping and key components.
4. **E2E (Playwright, TS):** Playwright's `webServer` runs the production build served by Uvicorn; several browser contexts with mobile emulation (Pixel 7): create → two players join → categories → vote → reveal; reload in the middle of voting. Chromium only in CI; WebKit optional locally.

### 15. Orchestration with a Makefile
A root `Makefile` is the single entry point for people, CI and Claude:
- `make setup` → `uv sync` + `pnpm install` + `playwright install chromium`
- `make dev` → Uvicorn with `--reload` + Vite dev (in parallel)
- `make gen` / `make gen-check` → Pydantic contract → TS
- `make lint` (Ruff + Biome), `make typecheck` (mypy + tsc), `make test` (pytest + Vitest), `make build` (Vite), `make e2e` (Playwright)
- `make verify` → `gen-check lint typecheck test e2e`, stopping at the first failure

### 16. Packaging: multi-stage Docker image
```dockerfile
FROM node:26-slim AS web            # 1) build the PWA
RUN npm install -g pnpm@12.21.0     # Node 26 no longer ships corepack
WORKDIR /repo
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml tsconfig.base.json ./
COPY apps/web/package.json apps/web/
COPY packages/protocol/package.json packages/protocol/
COPY e2e/package.json e2e/
RUN pnpm install --frozen-lockfile --filter web...
COPY apps/web apps/web
COPY packages/protocol packages/protocol
RUN pnpm --filter web build

FROM python:3.14-slim AS runtime    # 2) Python runtime
COPY --from=ghcr.io/astral-sh/uv:0.13.9 /uv /bin/uv
WORKDIR /app
COPY apps/server/pyproject.toml apps/server/uv.lock apps/server/.python-version ./
RUN uv sync --frozen --no-dev --no-install-project
COPY apps/server/src ./src
RUN uv sync --frozen --no-dev
COPY --from=web /repo/apps/web/dist ./web
ENV PATH="/app/.venv/bin:$PATH" WEB_DIST_DIR=/app/web ENV=production PORT=8000
USER nobody
CMD ["sh", "-c", "exec uvicorn cuadrillapp.main:create_app --factory --host 0.0.0.0 --port ${PORT} --proxy-headers --forwarded-allow-ips='*' --workers 1"]
```
Docker avoids depending on Render's native runtime having both Node and Python, and the same image works locally, in CI and on any other provider (Fly.io, Cloud Run).

### 17. CI/CD
- **GitHub Actions** `ci.yml` on `pull_request` and `push` to main:
  - `verify` job: `astral-sh/setup-uv` pinned to an exact release (it publishes no major tags) with caching, Node from `.node-version` + pnpm through `pnpm/action-setup` (version from the `packageManager` field), pnpm store and Playwright browser caches, `make setup`, `make verify`; uploads the Playwright report as an artifact on failure.
  - `docker` job: `docker build` of the image and a smoke test (`docker run` + `curl /healthz`). It catches a broken Dockerfile before merging (it is not part of `make verify` because cloud sessions may not have Docker).
- **Public repository** (`akkerd/cuadrillapp`): rulesets are free on the Free plan, and secret scanning with push protection is enabled. Nothing sensitive lives in the repo (`delivery-pipeline` specs).
- **main ruleset**: PR required, `verify` and `docker` checks required, 0 approvals (single-person project), no force pushes or deletion.
- **Render Blueprint** (`render.yaml`): web service with `runtime: docker`, `plan: free`, `healthCheckPath: /healthz`, auto-deploy only when the commit's checks pass (`autoDeployTrigger: checksPass`). Render does not switch traffic to the new version until the health check responds → spec "No downtime from broken versions".
  - *Fallback* if that option is unavailable on the plan: auto-deploy off + a `deploy` job in Actions that calls Render's Deploy Hook after `verify` and `docker` pass on main (URL stored as a GitHub secret).
- `/healthz` returns `{"status": "ok", "version": RENDER_GIT_COMMIT}` → Claude (or the user) confirms which commit is in production.
- **Rollback:** revert through a PR (the normal flow) or "Rollback" to a previous deploy in the Render dashboard. Documented in the README.

### 18. Why GitHub + Render and not "Claude Artifacts"
Claude Artifacts publish pages hosted on claude.ai, the fastest option for a frontend prototype, but they do not run our own Python backend, have no repo or CI and do not exercise the real "PR → checks → deploy" flow that we want to evaluate.
Render compared with the alternatives: Fly.io no longer has a real free plan; Cloud Run needs a project with billing and federated identity to deploy from Actions; Railway is paid after the trial. Render's free plan supports Docker and WebSockets, and WebSocket messages count as traffic, so the service does not go to sleep during a game.

### 19. Working with Claude from a phone
1. User: Claude app → Code → `cuadrillapp` repo → "make the reveal button bigger".
2. Cloud session: a SessionStart hook runs `scripts/cloud-setup.sh` (installs uv if missing and runs `make setup`), with no secrets.
3. Claude creates a branch, implements, runs `make verify`, pushes and opens a PR with a short summary (and Playwright screenshots if the change is visual).
4. Green CI → the user merges from the GitHub app (or asks Claude to).
5. Render deploys after the checks; Claude checks that `/healthz` returns the merged SHA.
`CLAUDE.md` sets these rules: never push to main, `make verify` before pushing, OpenSpec specs as the source of truth, player-facing text in `copy.ts`, `make gen` after touching `protocol/`, no `await` between reading and storing a room, English everywhere except the UI copy. Complements: Remote Control of the laptop session, and Claude's GitHub Action for `@claude` in issues (optional, needs a secret; out of scope for this change).

### 20. Basic security
Same origin (no CORS; Socket.IO's `cors_allowed_origins` limited to the same origin), a security-headers middleware (CSP `self`, `X-Content-Type-Options`, `Referrer-Policy`, `X-Frame-Options`, `Permissions-Policy`), Pydantic validation with `extra="forbid"` on every payload, a per-socket rate limit (in-memory token bucket) and a per-IP limit on room creation, tokens from `secrets`, logs without tokens. FastAPI's docs are disabled in production. No personal data is stored in this change.

### 21. Scaling path (not implemented)
Today: 1 instance, 1 worker, in-memory state. Scaling out only means swapping pieces behind interfaces that already exist; domain, handlers and frontend do not change:
1. `RedisRoomStore` (implements `RoomStore`), with a per-room lock (Redis `SET NX` with TTL) around get → apply → put.
2. `socketio.AsyncRedisManager` as `client_manager`, so a broadcast reaches sockets connected to other instances.
3. WebSocket-only transport on the client (no long-polling) to avoid sticky sessions, or a load balancer with affinity.
4. A Redis-backed `Scheduler` (keys with expiry) instead of in-memory `call_later`.
5. Several instances or `--workers N` in Uvicorn.

## Risks / Trade-offs

- [A deployment closes active rooms] → Do not merge during a party; the client shows "room closed" and goes back home with one tap. The scaling path (Redis) would solve it.
- [Render free cold start (~1 min after 15 min without traffic)] → "Waking up" screen with retries; the admin opens the app a minute early.
- [Slower Docker builds and limited build minutes on the free plan] → Layer caching (dependencies before code); deployments only from main.
- [Render's "deploy after checks" option not verified on the free plan] → Checked in the first CD task; the Deploy Hook fallback is already designed.
- [Two toolchains (uv + pnpm) in cloud sessions] → A single `make setup` and the environment setup script; tested in task 10.1.
- [Python ↔ TS contract drift] → Generated types + `make gen-check` in CI.
- [An accidental `await` between reading and storing a room breaks atomicity] → Rule in `CLAUDE.md`, a single mutation path in the hub and a concurrency test.
- [iOS: no real fullscreen, no install prompt] → Standalone + safe areas + mini install guide.
- [Disconnects when the phone locks] → Wake Lock + reconnection with a token + 60 s grace before admin succession.
- [E2E only on Chromium in CI] → Manual test on an iPhone before each real use; WebKit optional locally.

## Migration Plan

New project, no data migration. Rollout:
1. Done: public repo `akkerd/cuadrillapp` created, with secret scanning and push protection; commits authored with the GitHub noreply email.
2. User: creates a Render account and connects the Blueprint (`render.yaml`) to the repo (once, from the dashboard).
3. Claude configures the main ruleset and verifies the first deployment with `/healthz`.
4. User: installs the Claude/GitHub app on the repo and configures the cloud environment with the setup script.
Rollback: see decision 17.

## Open Questions

- Cuadrillapp logo. It does not affect specs or tasks.
- A custom domain instead of `*.onrender.com`? It can be added later in Render without code changes.
