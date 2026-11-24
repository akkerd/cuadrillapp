# Spec Delta

## Purpose

Defines who is in a room and how they appear: a profile with emoji and name, the candidate or voter-only role, manual participants without a phone, and how people leave or are removed from a room.

## ADDED Requirements

### Requirement: Participant profile
On entering a room, each participant SHALL pick an emoji from a curated list of funny emojis (with a random-emoji button) and a name of 1 to 16 characters. The system MUST remember the last emoji and name used on the device and suggest them next time.

#### Scenario: Random emoji
- **WHEN** the visitor taps the dice button on the profile screen
- **THEN** the emoji changes to another one from the list at random

#### Scenario: Remembered profile
- **WHEN** a visitor who played before on that device enters another room
- **THEN** the emoji and name are prefilled and they can join with a single tap

### Requirement: Unique name in the room
The name MUST be unique within the room, ignoring letter case, accents and extra spaces. Several participants MAY have the same emoji.

#### Scenario: Duplicate name
- **WHEN** a visitor tries to join as "dani" and there is already a "Dani" in the room
- **THEN** the system rejects the profile with a short "name taken" notice

### Requirement: Participant role
Each participant SHALL have a role: **candidate** (receives scores and also scores) or **voter-only** (scores but does not receive scores). The default role is candidate. Participants can change their own role, and admins anyone's role, only while the room is in the lobby.

#### Scenario: Role change in the lobby
- **WHEN** a participant switches their role to voter-only during the lobby
- **THEN** nobody sees them as a candidate any more

#### Scenario: Role locked during voting
- **WHEN** a participant tries to change their role while voting is open
- **THEN** the system does not allow the change

### Requirement: Joining while voting is open
The system SHALL allow joining a room in any phase. Someone who joins during voting picks a role while creating their profile and can vote immediately; if they join as a candidate, the others can score them.

#### Scenario: Late candidate
- **WHEN** someone joins as a candidate while voting is open
- **THEN** they appear in the list of candidates to score for every other voter

### Requirement: Manual participants
Admins SHALL be able to add manual participants (people without a phone) by giving an emoji, a name and a role. Manual participants count towards the room limit, are shown with a "no phone" indicator, never disconnect and can never be admins.

#### Scenario: Adding a friend without a phone
- **WHEN** an admin adds "Grandma 👵" as a candidate
- **THEN** she appears in the list with the "no phone" indicator and the others can score her

### Requirement: Leaving the room
A participant SHALL be able to leave voluntarily after confirming. Leaving removes them from the room together with the scores they gave and received, unless the room is in the results phase, in which case the revealed results do not change.

#### Scenario: Leaving during voting
- **WHEN** a candidate leaves while voting is open
- **THEN** they disappear from the list and the scores they gave and received are discarded

#### Scenario: Leaving after the results
- **WHEN** a participant leaves while the room shows the results
- **THEN** the results shown to everyone else do not change

### Requirement: Kicking participants
Admins SHALL be able to remove any other participant from the room (manual participants and other admins included) after confirming. The kicked participant MUST see a short "you're out" notice and return to the home screen; their scores are handled as if they had left. The kicked participant MAY join again with the code as a new participant.

#### Scenario: Kick
- **WHEN** an admin kicks a connected participant
- **THEN** the participant disappears from everyone's list and their phone shows the kick notice

#### Scenario: An admin cannot kick themselves
- **WHEN** an admin opens the actions on their own profile
- **THEN** the kick option is not shown
