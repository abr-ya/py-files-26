# CLI Resumable Upload Delta

## ADDED Requirements

### Requirement: Configurable CLI Server Target

The CLI MUST allow a user running on a local machine to target a py-files server by providing an API base URL.

#### Scenario: Login with explicit server URL

- **GIVEN** the py-files API is available at a network URL
- **WHEN** the user runs `pyfiles --base-url <url> login` with valid credentials
- **THEN** the CLI authenticates against that server
- **AND** stores the normalized base URL and access token in local user config for later commands

#### Scenario: Upload uses saved server URL

- **GIVEN** the user previously logged in with `--base-url <url>`
- **WHEN** the user runs `pyfiles upload ./file.bin` without `--base-url`
- **THEN** the CLI uses the saved server URL and token
- **AND** uploads to that server

#### Scenario: Missing server URL is clear

- **GIVEN** no server URL has been saved in local config
- **WHEN** the user runs `pyfiles upload ./file.bin` without `--base-url`
- **THEN** the CLI exits before reading file bytes
- **AND** reports that `--base-url` or prior login configuration is required

### Requirement: Resumable CLI Upload Sessions

The CLI and server MUST support resumable upload for authenticated CLI uploads using upload sessions and contiguous byte offsets.

#### Scenario: Create and complete upload session

- **GIVEN** the user is authenticated with the CLI
- **WHEN** the user uploads a file within `MAX_UPLOAD_BYTES`
- **THEN** the CLI creates an upload session
- **AND** sends file bytes with `Upload-Offset`
- **AND** completes the session into a `StoredUploadObject`

#### Scenario: Resume after interrupted upload

- **GIVEN** a CLI upload was interrupted after the server accepted some bytes
- **WHEN** the user retries the upload for the same local file
- **THEN** the CLI continues from the server-accepted offset when the local file still matches the session metadata
- **AND** does not resend bytes already accepted by the server

#### Scenario: Offset mismatch reports expected position

- **GIVEN** the CLI sends a chunk with an `Upload-Offset` that does not match the session's received byte count
- **WHEN** the server rejects the chunk
- **THEN** the response indicates an offset mismatch
- **AND** the CLI reports or uses the server's expected offset for retry
