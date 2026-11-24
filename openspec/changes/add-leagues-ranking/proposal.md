# Proposal

## Why

The same group of friends plays contests again and again (every party, every dinner), but with ephemeral rooms nobody remembers who won what. We want to group contests into private **leagues** per friend group and show a cumulative ranking, without forcing players to create accounts: only the person who creates contests that are saved signs in with Google.

It depends on `add-live-voting` (live rooms, voting and results) and is implemented after it.

## What Changes

- Google sign-in (optional to play, required to create contests that are saved).
- **Leagues**: every saved contest belongs to a league; whoever plays a contest in a league becomes a member of that league.
- When a signed-in user creates a room, the system suggests the league: if the user has not taken part in any, a new one is created; if they have taken part in one, it is preselected; if in several, all of them are shown. They can also create a new league or play without saving.
- When joining a league room, the player sees the league's players to pick themselves ("Who are you?") or create a new one; identity across contests is recognised by normalised name.
- When the results of a league room are revealed, the final scores and positions are saved (never individual scores).
- League ranking with a medal table (🥇🥈🥉), mean, best score and contest history, visible only to league members.
- Basic league management by its owner: rename the league, rename and merge players, delete contests.
- A persistent database (free managed Postgres) for accounts, leagues and results.

## Capabilities

### New Capabilities

- `accounts`: Google sign-in and sign-out, minimal data, linking the device's participations, and test sign-in outside production.
- `leagues`: league creation, choosing a league when creating a room, membership, player identity by name and the "Who are you?" picker, private access and owner management.
- `league-ranking`: saving results on reveal, computing and showing the league ranking, and the contest history.

### Modified Capabilities

None. The behaviour of `rooms`, `participants` and `results` defined in `add-live-voting` stays the same; rooms without a league keep working as before.

## Impact

- Server: database (schema, migrations), authentication, REST API for leagues, user session on the real-time connection.
- Web: sign-in button and avatar, league picker when creating, "Who are you?" picker on the profile, league and ranking screens, a league button on the results screen.
- Infrastructure: a Neon Postgres project (free), a Google OAuth client (manual step for the user in Google Cloud Console), new environment variables in Render. CI and Claude cloud sessions still need no secrets (SQLite in tests, ephemeral Postgres in CI and test sign-in).
- Personal data: name, email and Google avatar of whoever signs in; player names and emojis within each league.

## Out of Scope

- A public ranking across leagues, or leagues open to strangers.
- Other sign-in providers (Apple, email/password).
- Saving individual scores or per-voter statistics.
- Per-category statistics across the league (only each contest's final score counts for the ranking).
- Inviting people to a league without them having played one of its contests.
