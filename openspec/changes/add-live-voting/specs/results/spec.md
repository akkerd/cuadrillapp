# Spec Delta

## Purpose

Defines how a contest's results are computed and shown: per-category mean, final score, rankings with ties, the podium reveal and how to keep playing afterwards.

## ADDED Requirements

### Requirement: Per-category mean
A candidate's score in a category SHALL be the arithmetic mean of the scores received in that category, together with the number of scores received. If they received none, their score in that category is empty.

#### Scenario: Simple mean
- **WHEN** a candidate receives 6.00, 7.50 and 9.00 in "funny"
- **THEN** their mean in "funny" is 7.50 from 3 scores

### Requirement: Final score
A candidate's final score SHALL be the mean of their per-category means, counting only the categories where they received at least one score. A candidate with no scores at all is listed last in the overall ranking as having no votes.

#### Scenario: Final score with two categories
- **WHEN** a candidate has 7.50 in "funny" and 8.50 in "style"
- **THEN** their final score is 8.00

#### Scenario: Candidate without votes
- **WHEN** a candidate received no scores
- **THEN** they appear last in the overall ranking, marked as having no votes

### Requirement: Rankings and ties
The system SHALL sort candidates from highest to lowest score in an overall ranking and in a ranking for each category. Comparisons MUST use the exact value, and ties share a position (for example 1, 1, 3). Scores are displayed rounded to 2 decimals.

#### Scenario: Tie for first place
- **WHEN** two candidates have exactly the same highest final score
- **THEN** both appear in position 1 and the next one in position 3

### Requirement: Reveal the results
An admin SHALL close voting and reveal the results with a single button. On reveal, the results are computed and frozen, and every device shows at the same time an animated podium that uncovers third, second and first place, with confetti for the winner.

#### Scenario: Synchronised reveal
- **WHEN** an admin taps the reveal button
- **THEN** every participant sees the podium animation at the same time and nobody can change scores

#### Scenario: Reduced motion
- **WHEN** the device has the reduce-motion preference enabled
- **THEN** the podium is shown without animation or confetti

### Requirement: Browsing the results
In the results phase, each participant SHALL be able to see the overall ranking and each category's ranking, with each candidate's mean and number of scores, without seeing individual scores.

#### Scenario: Category tab
- **WHEN** a participant taps the "😂 funny" tab in the results
- **THEN** they see that category's ranking with means and number of scores

### Requirement: Reopen and new round
From the results, an admin SHALL be able to reopen voting keeping all scores, or start a new round that goes back to the lobby keeping participants and categories and clearing all scores.

#### Scenario: Reopen
- **WHEN** an admin taps the reopen button
- **THEN** the room goes back to voting with the previous scores intact and editable

#### Scenario: New round
- **WHEN** an admin taps the new-round button and confirms
- **THEN** the room goes back to the lobby with the same participants and categories and no scores
