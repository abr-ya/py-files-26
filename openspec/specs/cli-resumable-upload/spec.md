# cli-resumable-upload Specification

## Purpose
Define the accepted CLI authentication foundation and server-side resumable upload-session protocol for local `pyfiles` clients.

## Requirements
### Requirement: Configurable CLI Server Target

The CLI MUST allow a user running on a local machine to target a py-files server by providing an API base URL.

#### Scenario: Login with explicit server URL

- **GIVEN** the py-files API is available at a network URL
- **WHEN** the user runs `pyfiles --base-url <url> login` with valid credentials
- **THEN** the CLI authenticates against that server
- **AND** stores the normalized base URL and access token in local user config for later commands

#### Scenario: Login stores reusable server URL

- **GIVEN** the user previously logged in with `--base-url <url>`
- **WHEN** the login command completes successfully
- **THEN** the CLI stores the saved server URL and token for later commands

#### Scenario: Login requires server URL

- **GIVEN** no server URL has been saved in local config
- **WHEN** the user runs `pyfiles login` without `--base-url`
- **THEN** the CLI exits before sending credentials
- **AND** reports that `--base-url` is required

### Requirement: Server Resumable Upload Sessions

The server MUST support authenticated resumable upload sessions using contiguous byte offsets.

#### Scenario: Create and complete upload session through API

- **GIVEN** the user is authenticated
- **WHEN** the client creates an upload session and appends all bytes with contiguous `Upload-Offset` values
- **THEN** the server accepts the chunks
- **AND** completes the session into a `StoredUploadObject`

#### Scenario: Offset mismatch reports expected position

- **GIVEN** the client sends a chunk with an `Upload-Offset` that does not match the session's received byte count
- **WHEN** the server rejects the chunk
- **THEN** the response indicates an offset mismatch
- **AND** reports the server's expected offset

#### Scenario: Oversized session is rejected

- **GIVEN** the requested upload size exceeds `MAX_UPLOAD_BYTES`
- **WHEN** the client creates an upload session
- **THEN** the server rejects the request
- **AND** does not create a partial upload file
