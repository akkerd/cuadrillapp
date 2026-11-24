# Spec Delta

## Purpose

Lets people sign in with a Google account to create contests that are saved into leagues and to see their leagues from any device, while playing still needs no account.

## ADDED Requirements

### Requirement: Google sign-in
The system SHALL let users sign in with a Google account from the home screen with a sign-in button. After signing in, the app MUST show the user's avatar instead of the button and keep the session when the app is closed and reopened.

#### Scenario: Successful sign-in
- **WHEN** a visitor taps the sign-in button and authorises with their Google account
- **THEN** they return to the app with their avatar visible on the home screen

#### Scenario: Persistent session
- **WHEN** a signed-in user closes the app and opens it again days later
- **THEN** they are still signed in

#### Scenario: Sign-in cancelled
- **WHEN** the visitor cancels the authorisation at Google
- **THEN** they return to the home screen signed out, with a short notice

### Requirement: Sign out
A signed-in user SHALL be able to sign out from their avatar menu. Signing out MUST NOT affect the rooms they are playing in.

#### Scenario: Sign out
- **WHEN** the user taps sign out in the avatar menu
- **THEN** the app shows the sign-in button again

### Requirement: Playing without an account
Joining a room, voting and seeing the results SHALL keep working without signing in, both in rooms without a league and in league rooms.

#### Scenario: Guest in a league room
- **WHEN** a visitor who is not signed in joins a league room with the code
- **THEN** they can pick their player, vote and see the results without being asked to sign in

### Requirement: Minimal data
From the Google account, the system MUST store only the account identifier, the name, the email and the avatar URL, and MUST NOT show the email to other users.

#### Scenario: Private email
- **WHEN** another league member looks at the ranking
- **THEN** they do not see any user's email

### Requirement: Linking the device's participations
On sign-in, the system SHALL link to the account the league players that the device used in previous contests, as long as those players are not already linked to another account.

#### Scenario: Played as a guest, then signed in
- **WHEN** someone who played as "Lucas" in the "Cousins" league from their phone without signing in later signs in on that phone
- **THEN** the "Cousins" league appears among their leagues and "Lucas" is linked to their account

### Requirement: Test sign-in outside production
The system SHALL offer a test sign-in without Google, only when running outside production with test sign-in explicitly enabled, so that automated tests and development sessions need no real credentials. In production it MUST always be disabled.

#### Scenario: Production
- **WHEN** the service starts in production with test sign-in enabled by mistake
- **THEN** the service refuses to start and logs the reason
