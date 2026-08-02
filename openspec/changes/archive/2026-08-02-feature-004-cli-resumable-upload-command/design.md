# Design: CLI Resumable Upload Command

## Existing Context

Feature `003` provides:

- `POST /api/v1/upload-sessions`
- `PATCH /api/v1/upload-sessions/{session_id}` with `Upload-Offset`
- `POST /api/v1/upload-sessions/{session_id}/complete`
- `pyfiles --base-url <url> login`
- local CLI config with `base_url` and `access_token`

## CLI Flow

`pyfiles upload <path>` resolves the server URL in this order:

1. command-line `--base-url`
2. saved local config from a previous successful login
3. clear configuration error before reading file bytes

The command loads the saved token, checks the local file size, creates or resumes an upload session, sends fixed-size chunks with `Upload-Offset`, and completes the session. On success, it prints the stored object ID or a concise completion message.

`pyfiles status` uses the same server URL resolution order as upload, but it does not require or validate a saved token. It sends `GET /health` to the configured server, prints a concise success message when the server responds with a healthy `200` response, and returns a non-zero exit code for missing configuration, network errors, timeouts, or non-`200` health responses.

## Retry Metadata

The CLI stores retry metadata under the py-files config directory. Metadata should include local path, size, modified time, session ID, expected size, and last known server offset. The CLI may resume only when the local file still matches the saved metadata.

Offset mismatch responses with `expected_offset` should update the local offset and retry from that byte when the local file still matches.

## Error Handling

- Missing base URL or token: fail before reading file bytes with a clear message.
- Missing server URL for `pyfiles status`: fail before contacting the network with a clear message.
- Missing local file: fail before contacting the server.
- Oversized file: fail clearly when the server rejects session creation.
- Authentication failure: fail without appending chunks.
- Network interruption: preserve retry metadata and return a non-zero exit code.

## Verification

- CLI tests cover missing base URL/token, explicit `--base-url`, saved config reuse, status preflight success/failure, happy-path upload, offset mismatch handling, and retry metadata.
- A smoke test can run `pyfiles login --base-url ...` then `pyfiles upload ...` against a running local API.
