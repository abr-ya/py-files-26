# Tasks: Feature 003 CLI Resumable Upload

## Server

- [x] T021 Implement `POST /api/v1/upload-sessions`, `PATCH /api/v1/upload-sessions/{session_id}`, and `POST /api/v1/upload-sessions/{session_id}/complete` in `server/src/py_files_server/api/routes/upload_sessions.py`.
- [x] T022 Implement contiguous chunk append, received byte accounting, ownership checks, and upload-session state transitions in `server/src/py_files_server/services/upload_session_service.py`.
- [x] T023 Implement session finalization that promotes a complete partial file into `StoredUploadObject`, computes or verifies optional sha256, and cleans up partial storage in `server/src/py_files_server/services/upload_finalize.py`.

## CLI

- [x] T024 Implement the `pyfiles` argparse root in `clients/python/src/py_files_cli/__main__.py`, including global `--base-url` resolution.
- [x] T025 Implement `clients/python/src/py_files_cli/commands/login.py` to authenticate against the configured server and store the JWT plus normalized base URL in user config.
- [ ] T026 Implement `clients/python/src/py_files_cli/commands/upload.py` with resumable upload-session create/append/complete flow, progress output, interruption-safe retry metadata, and clear exit codes.

## Tests And Docs

- [x] T026a Add focused server tests for session create, append, offset mismatch, complete, ownership denial, and size limit behavior.
- [ ] T026b Add CLI tests for missing base URL, explicit `--base-url`, saved config reuse, login storage, and resumable upload retry behavior.
- [ ] T026c Update `clients/python/README.md` and `specs/001-network-file-upload-client/quickstart.md` with runnable CLI login/upload examples using `--base-url`.
- [ ] T026d Run targeted server and CLI validation, then record exact commands in the closeout.
