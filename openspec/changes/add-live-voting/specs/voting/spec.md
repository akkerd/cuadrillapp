# Spec Delta

## Purpose

Defines how a contest is voted: categories, phases, a 0-10 score in 0.25 steps per candidate and category, proxy voting for participants without a phone, visible progress and anonymous scores.

## ADDED Requirements

### Requirement: Categories
Admins SHALL be able to create, edit, reorder and delete categories while the room is in the lobby. Each category has an emoji and a name of 1 to 20 characters. A room allows 1 to 8 categories, and the system MUST offer quick suggestions (for example funny, original, effort, style).

#### Scenario: Add a suggested category
- **WHEN** an admin taps the "😂 funny" suggestion
- **THEN** the category is added and everyone sees it in the lobby

#### Scenario: Categories locked
- **WHEN** an admin tries to add or delete a category while voting is open
- **THEN** the system does not allow it

### Requirement: Contest phases
The room SHALL go through the phases lobby → voting → results, and only admins change the phase. To open voting there MUST be at least 1 category, at least 1 candidate and at least 2 participants.

#### Scenario: Start without categories
- **WHEN** an admin tries to start voting without categories
- **THEN** the button is disabled and shows what is missing

#### Scenario: Start voting
- **WHEN** an admin taps the vote button and the requirements are met
- **THEN** every device moves to the voting screen at the same time

### Requirement: Score scale
Each score SHALL be a value between 0 and 10, both included, in 0.25 steps (for example 7.25). The system MUST reject any other value and MUST display scores using the UI language's decimal separator.

#### Scenario: Valid score
- **WHEN** a voter gives a candidate 7.25 in a category
- **THEN** the score is saved and shown as 7.25 in the UI's number format

#### Scenario: Score off the scale
- **WHEN** a client sends a score of 7.3 or 10.25
- **THEN** the system rejects it

### Requirement: What each voter scores
During voting, each participant SHALL be able to score every candidate in every category, except themselves. Scoring is optional per candidate and category.

#### Scenario: No self-vote
- **WHEN** a candidate opens the voting screen
- **THEN** they do not appear among the candidates to score, and the system rejects any score for themselves

### Requirement: Touch score control
The voting screen SHALL let voters set each score with a 0-10 slider that moves in 0.25 steps and with −0.25 and +0.25 buttons, showing the value in large type next to an emoji that reflects the score. An unset score is shown as "—" and can be cleared.

#### Scenario: Fine adjustment
- **WHEN** a voter has 7.00 and taps "+"
- **THEN** the score becomes 7.25

### Requirement: Saving and editing scores
Each score SHALL be saved on the server as soon as it changes, with no submit button, and the voter MAY change or clear it while voting stays open.

#### Scenario: Change of mind
- **WHEN** a voter changes a score from 6.00 to 8.50 while voting is open
- **THEN** only the 8.50 score counts

#### Scenario: Voting closed
- **WHEN** a voter tries to change a score after the results are revealed
- **THEN** the system rejects the change

### Requirement: Proxy voting
Admins SHALL be able to score on behalf of any manual participant by selecting "vote as" that participant. The self-vote rules apply to the represented participant.

#### Scenario: Admin votes for Grandma
- **WHEN** an admin selects "vote as Grandma 👵" and scores other candidates
- **THEN** the scores count as Grandma's, and Grandma does not appear among the candidates to score in that mode

### Requirement: Progress and "done"
Each voter SHALL see how many scores they have given out of the total possible and MAY mark themselves as done, while still being able to edit until voting closes. All participants MUST see who is done, and admins also see each voter's numeric progress.

#### Scenario: Mark as done
- **WHEN** a voter taps the done button
- **THEN** everyone sees a check mark next to their avatar

#### Scenario: Progress for admins
- **WHEN** an admin looks at the list during voting
- **THEN** they see next to each voter how many scores they have given, for example "7/12"

### Requirement: Anonymous scores
No participant, admins included, SHALL be able to see the individual scores given by another participant. Participants only see their own scores and, for admins, those cast on behalf of manual participants.

#### Scenario: Other people's scores hidden
- **WHEN** an admin reads the room state during voting
- **THEN** they do not receive the scores given by other participants with a phone
