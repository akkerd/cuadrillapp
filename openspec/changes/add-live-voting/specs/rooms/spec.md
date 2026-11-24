# Spec Delta

## Purpose

Lets people create real-time contest rooms identified by a short code, join them from a phone, and stay connected even when the phone locks or switches apps.

## ADDED Requirements

### Requirement: Create a room
The system SHALL let any visitor create a new room. The creator joins as the first participant and as admin, and the room starts in the lobby phase.

#### Scenario: Successful creation
- **WHEN** a visitor taps "Create" and completes their profile
- **THEN** the system creates a room in the lobby phase, assigns it a unique code and shows the visitor inside it as admin

### Requirement: Room code
Each room SHALL have a 5-character uppercase code without ambiguous characters (0, O, 1, I, L), unique among active rooms. Code input MUST ignore letter case and spaces.

#### Scenario: Code typed in lowercase
- **WHEN** a visitor types " abc23 " in the code field and room ABC23 exists
- **THEN** the system puts them in room ABC23

#### Scenario: Unknown code
- **WHEN** a visitor enters a code that matches no active room
- **THEN** the system shows a short "not found" notice and does not put them in any room

### Requirement: Share a room
Inside a room, the system SHALL show the code, a direct link and a QR code that opens that link, plus a button to share through the phone's apps when the device supports it.

#### Scenario: Join by link
- **WHEN** a visitor opens the direct link of an active room
- **THEN** the system takes them straight to creating their profile for that room, without asking for the code

### Requirement: Room title
The room SHALL have a short title (1-30 characters, a default title until changed) visible to everyone and editable only by admins.

#### Scenario: Admin changes the title
- **WHEN** an admin changes the title to "Halloween 🎃"
- **THEN** every participant sees the new title immediately

### Requirement: Real-time synchronisation
Every change to the room state SHALL be reflected on the devices of all connected participants in under 1 second on a normal network, without reloading the page.

#### Scenario: A new participant arrives
- **WHEN** a participant joins the room
- **THEN** the other participants see them appear in the list without doing anything

### Requirement: Automatic reconnection
A participant who loses the connection (network, screen lock, app switch or reload) SHALL keep their seat, profile, permissions and scores, and the system MUST automatically put them back in the same seat when the connection returns on the same device and browser.

#### Scenario: Page reload
- **WHEN** a participant reloads the app in the middle of voting
- **THEN** they are back in the room with the same profile and their scores intact, without typing the code or name again

#### Scenario: Visible disconnected state
- **WHEN** a participant loses the connection
- **THEN** the others see them dimmed as disconnected, but they stay in the list

### Requirement: Room end of life
The system SHALL delete a room after 30 minutes without any connected participant. A device that tries to return to a deleted room MUST see a "room closed" notice and the option to go back to the home screen.

#### Scenario: Abandoned room
- **WHEN** 30 minutes pass with no connected participants in a room
- **THEN** the room no longer exists and its code stops being valid

#### Scenario: Server restart
- **WHEN** the server restarts (for example during a deployment) and a participant tries to reconnect
- **THEN** they see the "room closed" notice and a button to go back home

### Requirement: Room limits
The system SHALL limit each room to 30 participants (manual ones included) and reject joins when the room is full, with a short "full" notice.

#### Scenario: Full room
- **WHEN** a visitor tries to join a room with 30 participants
- **THEN** the system rejects the join and shows the "full" notice

### Requirement: Abuse protection
The system MUST validate all data sent by clients, reject invalid data without changing the room, and limit the rate of actions per connection and of room creation per origin.

#### Scenario: Invalid data
- **WHEN** a client sends an action with malformed data (for example a score of 11)
- **THEN** the system rejects it with an error and the room state does not change

#### Scenario: Burst of actions
- **WHEN** a connection sends actions above the rate limit
- **THEN** the system rejects the excess actions without affecting the other participants
