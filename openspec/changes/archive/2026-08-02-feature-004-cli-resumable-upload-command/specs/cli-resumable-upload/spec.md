# CLI Resumable Upload Command Delta

## ADDED Requirements

### Requirement: CLI Resumable Upload Command

The CLI MUST upload local files to a configured py-files server using resumable upload sessions and contiguous byte offsets.

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
- **THEN** the CLI reports or uses the server's expected offset for retry

### Requirement: CLI Remote Server Status Preflight

The CLI MUST provide a lightweight command for checking whether the configured py-files server is reachable before upload.

#### Scenario: Status uses saved server URL

- **GIVEN** the user previously logged in with `--base-url <url>`
- **WHEN** the user runs `pyfiles status` without `--base-url`
- **THEN** the CLI checks the saved server URL's `/health` endpoint
- **AND** reports that the remote server is reachable when the server returns a healthy response

#### Scenario: Status supports explicit server URL

- **GIVEN** the py-files API is available at a network URL
- **WHEN** the user runs `pyfiles --base-url <url> status`
- **THEN** the CLI checks that server's `/health` endpoint
- **AND** does not require a saved token

#### Scenario: Status reports unreachable server

- **GIVEN** the configured server URL is missing, unavailable, or returns an unhealthy response
- **WHEN** the user runs `pyfiles status`
- **THEN** the CLI exits with a non-zero status
- **AND** reports a concise preflight failure reason
