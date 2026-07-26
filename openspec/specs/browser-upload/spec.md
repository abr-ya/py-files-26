# browser-upload Specification

## Purpose
Define accepted browser upload behavior, including authenticated upload, user-visible outcomes, retry guidance, and size-limit handling.

## Requirements
### Requirement: Browser Authenticated Upload

The system MUST provide an authenticated browser upload flow using login/password access and the existing web UI.

#### Scenario: Browser upload after login

- **GIVEN** the user is not authenticated
- **WHEN** the user signs in with valid login/password credentials and submits a file through the browser UI
- **THEN** the system accepts the authenticated upload request
- **AND** the browser reports a successful upload or a clear failure reason

#### Scenario: Multiple browser upload outcomes

- **GIVEN** the user is authenticated
- **WHEN** the user uploads multiple files in one browser session
- **THEN** each file receives its own success or error outcome

### Requirement: Browser Upload Failure Guidance

The browser upload flow MUST show clear guidance when a transfer fails and MAY rely on full retry instead of resumable upload.

#### Scenario: Browser transfer failure

- **GIVEN** an authenticated browser upload fails before completion
- **WHEN** the failure is reported to the user
- **THEN** the user sees a clear failure message
- **AND** the message allows the user to retry the full upload

### Requirement: Browser Upload Size Limit

The browser upload flow MUST enforce the configured per-object size limit and MUST NOT report oversized files as accepted.

#### Scenario: Oversized browser upload

- **GIVEN** an authenticated user selects a file larger than the configured maximum
- **WHEN** the browser upload is submitted
- **THEN** the system rejects the file
- **AND** the browser receives a clear size-limit error
