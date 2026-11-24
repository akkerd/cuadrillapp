# Spec Delta

## Purpose

Defines who controls a room: admin permissions, how they are granted and revoked, and how control passes on automatically so a room is never left without someone to run it.

## ADDED Requirements

### Requirement: Admin permissions
Only admins SHALL be able to: edit the title, manage categories, add manual participants, kick, change other people's roles, grant or revoke admin, vote on behalf of manual participants and change the contest phase. The system MUST reject these actions when sent by someone without permission.

#### Scenario: Action without permission
- **WHEN** a participant who is not an admin tries to start voting
- **THEN** the system rejects the action and the room does not change

#### Scenario: Hidden controls
- **WHEN** a participant without permissions views the lobby
- **THEN** they do not see the admin controls

### Requirement: Several admins
A room SHALL allow several admins at once. An admin can grant admin to any participant with a phone and revoke it from any other admin. Every admin is marked with a crown visible to everyone.

#### Scenario: Grant admin
- **WHEN** an admin grants admin to another participant with a phone
- **THEN** that participant shows the crown and sees the admin controls

#### Scenario: Manual participant
- **WHEN** an admin opens the actions on a manual participant
- **THEN** the option to make them admin is not shown

### Requirement: Always at least one admin
The system MUST prevent an admin from revoking their own permission if they are the room's only admin.

#### Scenario: Last admin
- **WHEN** the only admin tries to revoke their own permission
- **THEN** the system prevents it

### Requirement: Admin succession
When a room has no admin present, the system SHALL automatically make admin the connected participant with a phone who has been in the room the longest. An admin stops being present when they leave, are kicked, or have been disconnected for 60 seconds.

#### Scenario: The admin leaves
- **WHEN** the only admin leaves the room
- **THEN** the connected participant who joined earliest becomes admin and everyone sees the crown on them

#### Scenario: The admin briefly loses the connection
- **WHEN** the only admin disconnects and returns within 60 seconds
- **THEN** they remain the only admin and nobody else is promoted

#### Scenario: The admin takes too long to return
- **WHEN** the only admin has been disconnected for more than 60 seconds
- **THEN** the next participant in join order becomes admin; when the original admin returns, they keep their permission too

#### Scenario: Nobody with a phone is connected
- **WHEN** no participant with a phone is connected
- **THEN** nobody is promoted, and succession applies as soon as someone reconnects
