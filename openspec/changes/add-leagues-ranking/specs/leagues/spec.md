# Spec Delta

## Purpose

Groups the contests of the same friend group into private leagues, recognises each player across contests by name, and decides who can see and manage each league.

## ADDED Requirements

### Requirement: Create a room with or without a league
When tapping create, a signed-in user SHALL go through the league step. A visitor who is not signed in MUST be able to choose between signing in (to save into a league) and playing without saving (a room without a league, as in `add-live-voting`).

#### Scenario: Not signed in
- **WHEN** a visitor who is not signed in taps create
- **THEN** they see the options to sign in and to play without saving

#### Scenario: Quick room
- **WHEN** the visitor chooses to play without saving
- **THEN** a room without a league is created and its results are not saved

### Requirement: League suggestion when creating
The league step SHALL be based on the leagues the user has taken part in (as a player or owner): with none, it proposes creating a new league with an editable name; with one, it preselects it as the main option; with several, it shows them all ordered by most recent use. As secondary options it MUST offer a new league and no league.

#### Scenario: First time
- **WHEN** a user without leagues creates their first room
- **THEN** they are offered a new league with an editable default name and, on confirming, the room is linked to that league

#### Scenario: A single league
- **WHEN** a user who has only taken part in "Cousins" taps create
- **THEN** "Cousins" is preselected and they can create the room with one tap

#### Scenario: Several leagues
- **WHEN** a user who has taken part in three leagues taps create
- **THEN** they see all three, most recent first, and pick one

### Requirement: League shown in the room
A room linked to a league SHALL show the league's name to every participant throughout the game.

#### Scenario: Joining a league room
- **WHEN** someone enters a room of the "Cousins" league
- **THEN** they see "🏆 Cousins" in the room header

### Requirement: Pick a player when joining
When creating their profile in a league room, the participant SHALL see the league's existing players (emoji + name) under "Who are you?" to pick themselves with one tap, or a "new" option to type a name. Picking a player prefills its name and emoji, which can still be changed.

#### Scenario: I pick myself from the list
- **WHEN** Lucas, who played in the league before, joins and taps "🐸 Lucas" in the list
- **THEN** he enters with that name and emoji and his results in this contest add up to "Lucas" in the league

#### Scenario: Preselection
- **WHEN** a device or an account has already used a player of that league
- **THEN** that player is preselected

#### Scenario: Player in use
- **WHEN** a league player is already used by another participant in the room
- **THEN** they appear disabled in the list

### Requirement: Identity by name
Within a league, two participations with the same normalised name (ignoring case, accents and extra spaces) SHALL count as the same player. A new name that matches nobody creates a new player in the league when the results are saved.

#### Scenario: Types their name instead of picking it
- **WHEN** someone chooses "new" and types "lucas " in a league where "Lucas" exists
- **THEN** they are assigned the league's "Lucas" player

### Requirement: Players linked to an account
A league player linked to a Google account SHALL be selectable only from a device signed in with that account, or by an admin when adding them as a manual participant; everyone else sees them with a lock. When a signed-in user picks an unlinked player, the system MUST link it to that account.

#### Scenario: Locked player
- **WHEN** a guest tries to pick or type the name of a player linked to another account
- **THEN** the system does not allow it and shows a short "in use" notice with a lock

#### Scenario: Linking while playing
- **WHEN** a signed-in user picks the unlinked player "Sara"
- **THEN** "Sara" is linked to their account

### Requirement: League membership
Every participant of a league room, manual participants and voter-only participants included, SHALL become a league player when the contest's results are saved, and their device MUST remember its access to that league.

#### Scenario: Guest after the contest
- **WHEN** the results of a contest in which a guest took part are saved
- **THEN** that guest can open the league ranking from the leagues list on their device

### Requirement: Private league
A league SHALL be visible only to its members: signed-in users linked to a player or owning the league, and devices that took part in one of its contests. The system MUST NOT list leagues publicly and MUST answer any other access as if the league did not exist.

#### Scenario: Outside access
- **WHEN** someone who is not a member tries to open a league's address
- **THEN** they see a "not found" notice

#### Scenario: My leagues
- **WHEN** a member opens their leagues list
- **THEN** they only see the leagues they belong to

### Requirement: League management
The owner of a league (whoever created it) SHALL be able to rename it, rename players and merge two players into one. When merging, all results move to the player that is kept; the merge MUST be rejected if both players are linked to different accounts.

#### Scenario: Merging duplicates
- **WHEN** the owner merges "Dani" into "Daniel", keeping "Daniel"
- **THEN** "Dani" disappears and their contests count for "Daniel" in the ranking

#### Scenario: Merge not possible
- **WHEN** the owner tries to merge two players linked to different accounts
- **THEN** the system rejects the merge

### Requirement: Delete a saved contest
The league owner and whoever created the contest SHALL be able to delete a saved contest from the league after confirming; the ranking is recomputed without it.

#### Scenario: Test contest
- **WHEN** the owner deletes a test contest from the history
- **THEN** it disappears from the history and stops counting in the ranking
