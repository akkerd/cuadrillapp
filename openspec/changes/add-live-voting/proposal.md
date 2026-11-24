# Proposal

## Why

We want a fast, fun mobile app to run contests among friends (costumes, cooking, outfits…) where everyone scores from their own phone, without installing anything from an app store and without accounts. The project also tests a development workflow where changes are requested from a phone and Claude implements, tests and deploys them safely.

## What Changes

- New installable fullscreen PWA with a colourful, relaxed look (party-game style), buttons made of an icon plus a short word.
- Real-time rooms identified by a short code, with a link and a QR code to join.
- Per-room profile: a funny emoji plus a username; a **candidate** role (receives scores) or a **voter-only** role.
- Room administration: the creator is admin; admins can add manual participants (without a phone), remove people, vote on behalf of manual participants, change roles and grant or revoke admin rights. If no admin is left, the role passes to the next participant in join order.
- Categories defined by the admins (emoji + short name).
- Voting: each voter scores every candidate (except themselves) in every category with a score from 0 to 10 in 0.25 steps.
- Results revealed by an admin: per-category ranking and overall ranking with an animated podium.
- Delivery pipeline: CI on GitHub Actions, automatic deployment to Render only after green checks, a health check that reports the version, and a documented flow for Claude to make changes from cloud sessions (phone) through PRs.

## Capabilities

### New Capabilities

- `rooms`: room creation, code, link/QR, joining, reconnection, title, lifecycle and limits.
- `participants`: profile (emoji + name), candidate/voter roles, manual participants, leaving and being kicked.
- `room-admin`: admin permissions, granting and revoking admin, automatic succession.
- `voting`: categories, contest phases, 0-10 scoring in 0.25 steps, proxy voting, progress and anonymity.
- `results`: means, per-category and overall rankings, ties, reveal and new rounds.
- `app-shell`: PWA experience (installation, fullscreen, screen kept on, updates), language and tone of the UI.
- `delivery-pipeline`: CI checks, protected main, automatic and verifiable deployment, rollback and the change workflow with Claude.

### Modified Capabilities

None (new project).

## Impact

- New `cuadrillapp` repository (monorepo): `apps/server` (Python 3.14 + FastAPI + Socket.IO), `apps/web` (React), `packages/protocol` (TypeScript types generated from the backend), `e2e`.
- External dependencies: GitHub (repo, Actions), Render (free plan, one web service).
- No database and no personal data in this change: all room state lives in server memory.
- Manual steps for the user: `gh auth login`, create a Render account and connect the Blueprint, install the Claude/GitHub app on the repo.

## Out of Scope

- Leagues, Google accounts, persistence and global ranking (change `add-leagues-ranking`).
- Chat, sounds, custom themes and multiple languages.
- Horizontal scaling: a single process runs; the path to scale is described in `design.md` but not implemented.
- Offline play: the app needs a connection during a game.
