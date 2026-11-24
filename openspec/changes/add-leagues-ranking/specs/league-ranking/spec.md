# Spec Delta

## Purpose

Saves the result of every contest in a league and shows its members a cumulative ranking with a medal table, means and the contest history.

## ADDED Requirements

### Requirement: Save results on reveal
When the results of a league room are revealed, the system SHALL save the contest (title, date, categories) and, for each candidate, their final score, their position in the overall ranking and their per-category means. If voting is reopened and the results are revealed again, the save MUST replace the previous one for the same contest. A contest without any scores MUST NOT be saved.

#### Scenario: Saved on reveal
- **WHEN** an admin reveals the results in a room of the "Cousins" league
- **THEN** the contest appears in the "Cousins" history with its podium

#### Scenario: Revealing twice
- **WHEN** an admin reopens voting, scores change and the results are revealed again
- **THEN** the league has a single record of that contest with the new results

#### Scenario: New round in the same room
- **WHEN** an admin starts another round and reveals it
- **THEN** it is saved as a separate contest in the same league

### Requirement: Save failure
If saving fails, the results SHALL still be shown in the room, and admins MUST see a short "not saved" warning with a retry button.

#### Scenario: Database unavailable
- **WHEN** the database does not respond on reveal
- **THEN** everyone sees the podium and admins see the warning with the retry button

### Requirement: Score privacy
The system MUST NOT store individual scores or who scored whom; only the per-candidate aggregates described in "Save results on reveal".

#### Scenario: Stored data
- **WHEN** what was saved for a contest is inspected
- **THEN** it only contains means, positions and the number of scores per candidate

### Requirement: League standings
The league ranking SHALL include every player who has been a candidate in at least one saved contest, with: gold, silver and bronze medals (positions 1, 2 and 3 in each contest's overall ranking, shared on ties), contests played as a candidate, mean of their final scores and best final score. By default it MUST be ordered by golds, then silvers, then bronzes, then mean, from highest to lowest.

#### Scenario: Medal table
- **WHEN** Leo won 2 contests and Ana won 1 and came second in 3
- **THEN** Leo appears above Ana

#### Scenario: Shared tie
- **WHEN** two candidates tie for first place in a contest
- **THEN** both get a gold medal

#### Scenario: Voter only
- **WHEN** a league player has only taken part as a voter
- **THEN** they do not appear in the standings but can see the league

### Requirement: Order by mean
The user SHALL be able to switch the ranking order to mean (mean of final scores from highest to lowest) with one tap.

#### Scenario: Change the order
- **WHEN** a member taps the mean tab in the ranking
- **THEN** the list is reordered by mean of final scores

### Requirement: Contest history
The league SHALL show the history of saved contests, from newest to oldest, with title, date and podium, and tapping one MUST show its overall and per-category rankings as they were saved.

#### Scenario: Checking an old contest
- **WHEN** a member taps "Halloween 🎃" in the history
- **THEN** they see the overall and per-category rankings of that contest

### Requirement: Access from the results
On the results screen of a league room, the system SHALL show a "🏆 League" button that opens the league ranking, already updated with the contest just saved.

#### Scenario: Seeing the league after the reveal
- **WHEN** a participant taps the league button after the reveal
- **THEN** they see the league ranking including the contest that just ended
