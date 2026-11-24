# Spec Delta

## Purpose

Defines how a code change reaches production safely and verifiably, including when Claude makes it from a cloud session requested from a phone: mandatory checks, automatic deployment, version check and rollback.

## ADDED Requirements

### Requirement: Single verification command
The repository SHALL provide a single verification command that runs lint, type checking, unit and integration tests, the production build and end-to-end tests in an emulated mobile browser, and that exits with an error if any of them fails.

#### Scenario: Local or cloud verification
- **WHEN** a developer or Claude runs the verification command on a clean checkout after installing dependencies
- **THEN** every check runs and the result clearly states whether everything passed

### Requirement: Checks on every PR
Every pull request and every push to main SHALL automatically run the full verification in CI and publish the result as a commit check. If the end-to-end tests fail, the failure report MUST be downloadable from the run.

#### Scenario: PR with a broken test
- **WHEN** a PR that breaks a test is opened
- **THEN** the check shows red on the PR and the report can be downloaded

### Requirement: Protected main
The main branch MUST accept changes only through pull requests with a green verification check; direct pushes to main MUST be rejected.

#### Scenario: Direct push
- **WHEN** someone tries to push directly to main
- **THEN** GitHub rejects it

### Requirement: Automatic deployment after checks
Every commit that reaches main SHALL be deployed to production automatically only after its CI verification has passed; a commit with red checks MUST NOT be deployed.

#### Scenario: Merging a green PR
- **WHEN** a PR with green checks is merged into main and main's verification passes
- **THEN** the new version is deployed without manual intervention

### Requirement: No downtime from broken versions
The service SHALL expose a health endpoint that reports a healthy status and the identifier of the deployed commit. A deployment whose new version does not respond correctly on the health endpoint MUST NOT replace the version that is running.

#### Scenario: Check the deployed version
- **WHEN** the health endpoint is queried after a deployment
- **THEN** it responds healthy and reports the commit just merged into main

#### Scenario: Version that does not start
- **WHEN** the new version fails to start
- **THEN** the previous version keeps serving users

### Requirement: Rollback
The project SHALL document a rollback procedure that restores the previous version within minutes, either by reverting the commit on main through a PR or by reactivating a previous deployment at the hosting provider.

#### Scenario: Revert a broken change
- **WHEN** the revert of a problematic change is merged into main
- **THEN** the previous version is deployed through the same flow with checks

### Requirement: Change workflow with Claude
The repository SHALL include agent instructions that require working on a branch, running the full verification before publishing, opening a PR with a short summary and checking after the merge that the health endpoint shows the new commit. A Claude cloud session MUST be able to install dependencies and test browsers without manual steps or secrets.

#### Scenario: Change requested from the phone
- **WHEN** the user asks for a change to the repository from the Claude app on their phone
- **THEN** Claude implements it on a branch, passes the verification and opens a PR that the user can merge from the phone

### Requirement: No secrets in the repository
The repository and the CI logs MUST NOT contain secrets; sensitive configuration lives only in the hosting provider's environment variables or in GitHub secrets.

#### Scenario: Configuration review
- **WHEN** the repository files and CI logs are inspected
- **THEN** no credential or token appears

### Requirement: Public repository with secret scanning
The repository is public and SHALL have the provider's secret scanning and push protection enabled, so that a push containing a recognisable credential MUST be rejected before it is published.

#### Scenario: Push with a credential
- **WHEN** someone tries to push a commit containing a recognisable token
- **THEN** GitHub rejects the push and points to the file and line

### Requirement: No personal data in the repository
The repository MUST NOT contain personal data: no personal emails, no phone numbers, no data about participants of real games. Commits MUST be authored with the provider's private (noreply) email, and spec and test examples MUST use fictional names.

#### Scenario: Commit authorship
- **WHEN** the repository history is reviewed
- **THEN** no commit shows a personal email

### Requirement: English-only repository content
Everything in the repository (code, comments, documentation, specs, commit messages and pull request texts) MUST be written in English. The only exception is player-facing UI copy, which MUST live in a single UI copy module.

#### Scenario: Reviewing a pull request
- **WHEN** a pull request adds documentation, comments or tests
- **THEN** they are written in English, and any non-English text is limited to the UI copy module
