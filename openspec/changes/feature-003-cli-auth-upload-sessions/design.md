# Design: CLI Auth And Upload Sessions

## Existing Context

The accepted browser MVP already includes login/password auth, JWT bearer tokens, `StoredUploadObject`, `UploadSession`, filesystem blob storage under `STORAGE_ROOT`, and `POST /api/v1/objects` multipart upload.

The original contract already sketches resumable uploads:

1. `POST /api/v1/upload-sessions`
2. `PATCH /api/v1/upload-sessions/{session_id}` with `Upload-Offset`
3. `POST /api/v1/upload-sessions/{session_id}/complete`

## Server Flow

`POST /api/v1/upload-sessions` creates an owned `UploadSession` for the authenticated user with filename, expected size, optional checksum, received byte count `0`, and `active` state. It rejects sizes above `MAX_UPLOAD_BYTES`.

`PATCH /api/v1/upload-sessions/{session_id}` accepts `application/octet-stream` chunks. The server checks ownership, active state, and that `Upload-Offset` equals the currently recorded received byte count before appending bytes to the partial file. Offset mismatch returns `409` with the expected offset.

`POST /api/v1/upload-sessions/{session_id}/complete` verifies the received size, optional checksum when available, promotes the partial file to the blob layout, creates `StoredUploadObject`, marks the session complete, and removes or detaches the partial path.

## CLI Flow

The CLI exposes a global `--base-url` option. Commands resolve the server URL in this order:

1. command-line `--base-url`
2. saved local config from a previous successful login
3. no default for non-interactive upload; report a clear configuration error

`pyfiles login --base-url <url>` sends credentials to `/api/v1/auth/login`, then stores the normalized API base URL and JWT in the user's config directory, such as `~/.config/py-files/` on Unix or the platform equivalent.

`pyfiles upload <path>` is intentionally deferred to feature `004`. This feature stores the base URL and token in the same shape that the upload command will consume.

## Error Handling

- Authentication failure: fail without creating or appending a session.
- Oversized upload-session create requests: fail before creating a partial file.
- Offset mismatch: return the server-expected offset for the future CLI upload command.

## Verification

- Server tests cover session create, chunk append, offset mismatch, completion, ownership denial, and size limits.
- CLI tests cover base URL normalization, missing base URL for login, and login config write.
- A smoke test demonstrates `pyfiles login --base-url ...` against a running API.
