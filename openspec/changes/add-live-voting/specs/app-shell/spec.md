# Spec Delta

## Purpose

Defines the app experience on a phone: an installable fullscreen PWA, a party-game look with icons and short words, the screen kept on during a game, and the behaviour on slow connections or when a new version is deployed.

## ADDED Requirements

### Requirement: Installable app
The app SHALL be installable on the Android and iOS home screen with its own name, icon and colour, and when opened from the icon it MUST fill the whole screen without the browser bar (fullscreen where the system allows it, standalone otherwise).

#### Scenario: Open from the icon
- **WHEN** the user opens the installed app from the home screen
- **THEN** the app is shown without the browser's address bar

### Requirement: Installation help
If the app is used in the browser without being installed, the system SHALL offer an install button: on Android it triggers the native installation and on iOS it shows a two-step visual guide (Share → Add to Home Screen).

#### Scenario: iPhone without installing
- **WHEN** an iPhone user taps the install button in Safari
- **THEN** they see the mini guide with the Share and Add to Home Screen icons

### Requirement: Fullscreen from the browser
In browsers that support it, the system SHALL offer a button to toggle fullscreen without installing the app.

#### Scenario: Android in Chrome
- **WHEN** the user taps the fullscreen button in Chrome on Android
- **THEN** the app fills the whole screen

### Requirement: Screen kept on
While the user is inside a room, the system SHALL prevent the screen from turning off on devices that allow it, and release that lock when leaving the room.

#### Scenario: Long voting session
- **WHEN** a participant stays on the voting screen without touching the phone for several minutes
- **THEN** the screen stays on

### Requirement: Mobile design
The interface SHALL be designed for a phone in portrait (360 px wide and up), respect the safe areas (notch and gesture bar) and use touch targets of at least 44 px.

#### Scenario: iPhone with a notch
- **WHEN** the installed app opens on an iPhone with a notch
- **THEN** no control is hidden by the notch or the gesture bar

### Requirement: Visual tone and copy
The UI SHALL use a colourful, relaxed palette, a rounded typeface, emojis and smooth animations. Every button MUST combine an icon with at most two short words in the UI language; notices and errors MUST be one to three words with an emoji.

#### Scenario: Main buttons
- **WHEN** a user is on the home screen
- **THEN** they see buttons made of an icon and a single word (create, join), with no explanatory sentences

### Requirement: Connection status
The system SHALL show an unobtrusive indicator when the connection to the server is lost and retry on its own. If the server is slow to respond when the app opens (cold start), it MUST show an animated waiting screen instead of an error.

#### Scenario: Sleeping server
- **WHEN** a user opens the app and the server takes 40 seconds to start
- **THEN** they see a "waking up" animation and the app carries on by itself when the server responds

### Requirement: App updates
When a new version has been deployed, the system SHALL offer an update button and MUST NOT reload the app on its own while the user is inside a room.

#### Scenario: New version in the middle of voting
- **WHEN** a new version is deployed while a user is voting
- **THEN** the app does not reload and shows the update notice for the user to apply whenever they want

### Requirement: Basic accessibility
Text and buttons SHALL have enough contrast against the coloured backgrounds, icon-only buttons MUST have an accessible name, and animations MUST respect the reduce-motion preference.

#### Scenario: Screen reader
- **WHEN** a screen reader reaches an icon-only button
- **THEN** it announces its purpose (for example "share room")
