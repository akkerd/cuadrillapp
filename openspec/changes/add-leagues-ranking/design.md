# Design

## Context

Builds on the system from `add-live-voting` (see its `design.md`): one ASGI app (FastAPI + python-socketio) in a Docker image on Render, rooms in memory behind `RoomStore`, a pure domain, a single mutation path in the hub, per-viewer projected snapshots, `compute_results` with exact fractions and a Pydantic → TypeScript generated contract. Motivation is in `proposal.md`, behaviour in `specs/`.

New constraints:
- Durable, free persistence is needed: Render's free Postgres expires after 30 days and is deleted.
- CI and Claude cloud sessions must not need secrets; cloud sessions must not need Docker either.
- Sign-in must work in the installed PWA (iOS included).

## Goals / Non-Goals

**Goals:**
- Persist only what leagues and the ranking need; the live game stays in memory.
- The whole flow (sign-in included) must be testable end to end without Google or an external database.
- Keep playing without an account exactly as before.

**Non-Goals:**
- Persisting the state of live rooms.
- Fine-grained league roles beyond "owner" and "member".
- A global admin panel.

## Architecture (additions)

```
 PWA ──HTTPS──▶ ASGI app ─┬─ FastAPI
                          │   ├─ /api/auth/*      Authlib (Google OIDC) → signed cookie `cq_session`
                          │   ├─ /api/me*         current user, link devices
                          │   └─ /api/leagues*    routers with access dependencies
                          ├─ python-socketio      connect(): reads `cq_session` → user_id in the socket session
                          │    └─ on reveal: asyncio task → LeagueService.save_contest() (transaction)
                          └─ SQLAlchemy 2.0 async ──▶ prod: Neon Postgres (asyncpg)
                                                     dev/tests: SQLite (aiosqlite)
                                                     CI: + Postgres service container (`pg` suite)
```

New modules in `apps/server/src/cuadrillapp/`:

```
db/         engine.py (create_async_engine from DATABASE_URL), models.py (ORM), session.py
migrations/ Alembic (async env, render_as_batch for SQLite)
auth/       google.py (Authlib), cookies.py (sign/read cq_session), routes.py, test_login.py, deps.py
leagues/    service.py (save_contest, links), ranking.py (PURE), access.py (deps), routes.py
```

## Decisions

### 1. SQLAlchemy 2.0 async with Postgres (prod) and SQLite (dev/tests)
- **Production:** Neon free (managed, persistent Postgres with scale-to-zero). URL `postgresql+asyncpg://…?ssl=require`.
- **Development, tests and Claude sessions:** SQLite with `aiosqlite` (file or `:memory:`). Nothing to install, no Docker, no secrets.
- **CI:** besides the normal suite on SQLite, a step runs the tests marked `@pytest.mark.pg` against a GitHub Actions `postgres` service container to catch dialect differences.
- To keep portability real: generic SQLAlchemy types (`String` for UUID ids, `JSON`, `DateTime(timezone=True)`, `Float`), no Postgres-specific SQL, and ranking computations in Python (decision 8), not in SQL.
- *Alternatives:* PGlite (only exists for JS); `py-pglite` (needs Node at test time); `pytest-postgresql` (needs Postgres binaries in the cloud session); Render Postgres (expires); Supabase free (pauses after a week without use); SQLite in production (Render free has no persistent disk).

### 2. Alembic migrations on startup
`alembic revision --autogenerate` produces versioned migrations in the repo (async `env.py`, `render_as_batch=True` so they also apply on SQLite). The image's `CMD` becomes `alembic upgrade head && uvicorn …`: if a migration fails, the process does not start, the health check fails and Render keeps the previous version. Rule in `CLAUDE.md`: additive migrations only (expand/contract) so the previous version keeps working with the new schema during the deployment. Tests build the schema by applying the same migrations (not `create_all`), so a broken migration breaks CI.

### 3. Google sign-in: Authlib + a signed session cookie
- **OIDC with Authlib** (`authlib.integrations.starlette_client.OAuth`, a `google` registration with the discovery `server_metadata_url` and the `openid email profile` scopes). Routes:
  - `GET /api/auth/google/login` → full redirect (no popup) to Google with `state` and `nonce`.
  - `GET /api/auth/google/callback` → `authorize_access_token()` validates the ID token; upserts `users` by `google_sub`; sets the cookie; redirects to `/`. If the user cancelled, it redirects to `/?login=cancelled` (spec "Sign-in cancelled").
  - `POST /api/auth/logout` clears the cookie. `GET /api/me` returns the user or 401.
- Starlette's `SessionMiddleware` is used **only** for the temporary `state` of the OAuth flow.
- **User session:** our own `cq_session` cookie = `itsdangerous.URLSafeTimedSerializer(SESSION_SECRET).dumps({"uid": …})`, `HttpOnly`, `Secure`, `SameSite=Lax`, 30 days (spec "Persistent session"). No sessions table: revoking individual sessions is not needed for a project among friends; rotating `SESSION_SECRET` signs everyone out.
- FastAPI dependencies `optional_user` and `require_user` read and verify the cookie with `auth/cookies.py`.
- **Socket.IO:** the `connect(sid, environ, auth)` handler reads the `Cookie` header from `environ` with the same helper and stores `user_id` (or `None`) with `sio.save_session`. On sign-in or sign-out, the client reconnects the socket.
- **Test sign-in:** a `test_login` router (`POST /api/auth/test-login {name}`) included only if `settings.env != "production"` and `settings.auth_test_login`. A `Settings` validator raises an error if `ENV=production` and `AUTH_TEST_LOGIN` is set → the app does not start (spec "Production"). Used by pytest, Playwright and Claude sessions.
- *Alternatives:* `fastapi-users` (heavier, with sessions/JWT and tables we do not need); Google Identity Services with an ID token on the client (popup, worse in an iOS PWA); database sessions (per-session revocation not needed).
- *iOS PWA risk:* the OAuth redirect inside an installed PWA may open in an isolated Safari view. Mitigation: test it on a real device in the first auth task; if it fails, in standalone mode the sign-in button tells the user to sign in from Safari first, and this is documented.

### 4. Data model (ORM)

```
users            id, google_sub UNIQUE, name, email, avatar_url, created_at
leagues          id, name, emoji, owner_user_id → users, access_key UNIQUE, created_at, last_played_at
league_members   id, league_id → leagues, display_name, name_key, emoji, user_id → users NULL, created_at
                 UNIQUE(league_id, name_key), UNIQUE(league_id, user_id)
contests         id (generated when each round opens), league_id, title, host_user_id → users,
                 categories JSON [{emoji, name}], revealed_at, created_at
contest_entries  contest_id → contests, member_id → league_members, role ('candidate'|'voter'),
                 final_score FLOAT NULL, position INT NULL, scores_count INT,
                 category_scores JSON [{avg, count, position}]
                 PK(contest_id, member_id)
```
- `name_key` = the same `names.normalize_name()` used by the room domain (spec "Identity by name").
- Voter-only participants and candidates who received no scores get a row with `final_score NULL`: they count as members (access) without entering the standings.
- `position` is copied from `compute_results` (computed with exact fractions); `final_score` is stored as a float only to display and to sort by mean.

### 5. Leagues in the live room
- `room:create` accepts `league: {id} | {new_name} | null` and requires a `user_id` in the socket session unless it is `null`. **Atomicity rule:** database queries happen before reading the room (resolving or creating the league, loading its members) and the domain command is then applied synchronously, as everywhere else in the hub.
- The room stores `league: {id, name}`, the loaded members and the `contest_id` of the current round (a new one on every new round).
- The snapshot of a league room includes `league.members` (id, name, emoji, `locked` if linked to an account other than the viewer's, `taken` if another participant in the room already uses it), projected per viewer.
- `Participant.member_id` is optional: if the participant picked one, it is used; otherwise, on save it is resolved by `name_key` or created. The lock is validated on join and on profile changes (spec "Players linked to an account").
- League suggestion: `GET /api/leagues/mine` returns the user's leagues (owner or linked) ordered by `last_played_at`; the client applies the spec's 0/1/several rule.

### 6. Saving on reveal
After a reveal in a league room, the domain emits a `SaveContest(contest_id, results, participants)` effect. The realtime layer starts an `asyncio` task that runs `LeagueService.save_contest()` in a transaction (`async with session.begin()`): upsert members, delete and insert the `contest_entries` of that `contest_id` (idempotent across re-reveals), update `last_played_at` and the `user_id` links. When done, it applies an internal `save_status(ok|failed)` command through the hub and broadcasts the snapshot again; if it failed, admins see the "not saved" warning and `league:retry_save`. The service only receives the output of `compute_results`: individual scores never reach the persistence layer (spec "Score privacy").

### 7. Private access
- Signed-in users: a member if they own the league or have a `league_members.user_id` in it.
- Devices without a session: after saving, the server emits `league:grant {league_id, access_key, member_id}` to each participant, and the client stores it in `localStorage`. `access_key = secrets.token_urlsafe(16)`, unique per league.
- Dependency `league_access(league_id, user=Depends(optional_user), x_league_key: str | None = Header(None))`: grants access to members or when the key matches (`secrets.compare_digest`); otherwise `HTTPException(404)` (spec "Outside access"). `require_league_owner` for management.
- On sign-in, the client sends its grants to `POST /api/me/link-devices` and the server links the `member_id`s that have no `user_id` (spec "Linking the device's participations").

### 8. Ranking computed in Python
`leagues/ranking.py`: a pure function `compute_league_ranking(entries) -> list[RankingRow]` (golds, silvers and bronzes from `position` 1/2/3 with shared ties, contests played as a candidate, mean of `final_score`, best score; ordered by medals or by mean). The query only loads the league's `contest_entries` (few rows). Benefits: the same result on SQLite and Postgres, and direct unit tests for each scenario in `specs/league-ranking`.

### 9. REST API and frontend types
FastAPI routers with Pydantic input/output models: `GET /api/leagues/mine`, `GET /api/leagues/{id}` (ranking + history), `GET /api/leagues/{id}/contests/{contest_id}`, `PATCH /api/leagues/{id}`, `PATCH /api/leagues/{id}/members/{member_id}`, `POST /api/leagues/{id}/members/merge`, `DELETE /api/leagues/{id}/contests/{contest_id}`, `POST /api/me/link-devices`. `make gen` also exports `openapi.json` and generates REST types with `openapi-typescript` into `packages/protocol`; `make gen-check` covers both contracts.

### 10. Frontend
- Home: sign-in button (G) / avatar with a menu (leagues, sign out). The leagues list shows the account's leagues + the device's grants.
- Create: a bottom sheet with the spec's rule (new / preselected / list) + "new" and "no league".
- Profile in a league room: a "Who are you?" carousel of emoji + name chips (locked/taken disabled) + "new".
- Results: a league button. League screen: medal table with "medals" / "mean" tabs, history and an ✏️ owner mode.
- REST data with TanStack Query (cache and invalidation after `league:grant`).

### 11. Configuration and secrets
Variables in Render: `DATABASE_URL` (Neon), `SESSION_SECRET`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `PUBLIC_URL`. None of them in GitHub or in the repo. CI and Claude sessions: SQLite + `AUTH_TEST_LOGIN=1` (the Postgres job in CI uses the service container's ephemeral credentials, not secrets). A "Web" Google OAuth client with the redirect URIs `https://<app>.onrender.com/api/auth/google/callback` and `http://localhost:5173/api/auth/google/callback`; consent screen in "Testing" mode with the friends as test users, or published (basic scopes need no verification).

## Risks / Trade-offs

- [SQLite ↔ Postgres differences] → Generic types, computations in Python, migrations applied on both and a `pg` suite in CI against real Postgres.
- [asyncpg with Neon's pooler (PgBouncer in transaction mode) fails with prepared statements] → Use Neon's direct (non-pooled) endpoint or `connect_args={"statement_cache_size": 0}`; covered in the rollout task.
- [OAuth inside the iOS PWA] → Test on a real device; fallback documented in decision 3.
- [Ambiguous identity by name (two different "Dani")] → "Who are you?" picker, lock for linked players, and merge/rename by the owner.
- [Grants in `localStorage` are lost when data is cleared] → Signing in keeps the leagues; the owner always keeps access.
- [A leaked `access_key` gives read access] → Read-only and no emails; acceptable among friends. Future improvement: regenerate the key.
- [A database `await` slipping into the hub between reading and storing a room breaks atomicity] → I/O before reading the room or in separate tasks that come back through the hub; concurrency test.
- [Broken migration during a deployment] → The process does not start and Render keeps the previous version; additive migrations only.

## Migration Plan

1. Implement with SQLite and test sign-in (everything testable without external accounts).
2. User: creates the Neon project and the OAuth client in Google Cloud Console (guided steps in the README); Claude adds the variables in Render (or the user, if Claude has no access).
3. Merge → the image applies migrations on startup → check `/healthz` and a real sign-in from a phone.
4. Rollback: revert the PR. The new tables do not affect the previous version; the migration does not need undoing.

## Open Questions

- Default name for a new league ("<name>'s league" with a random emoji) and whether the league emoji is editable: a UI detail that does not change specs or tasks.
