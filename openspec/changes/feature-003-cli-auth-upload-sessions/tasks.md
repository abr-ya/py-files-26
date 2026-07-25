# Tasks: Feature 003 CLI Auth And Upload Sessions

## Server

- [x] T021 Implement `POST /api/v1/upload-sessions`, `PATCH /api/v1/upload-sessions/{session_id}`, and `POST /api/v1/upload-sessions/{session_id}/complete` in `server/src/py_files_server/api/routes/upload_sessions.py`.
- [x] T022 Implement contiguous chunk append, received byte accounting, ownership checks, and upload-session state transitions in `server/src/py_files_server/services/upload_session_service.py`.
- [x] T023 Implement session finalization that promotes a complete partial file into `StoredUploadObject`, computes or verifies optional sha256, and cleans up partial storage in `server/src/py_files_server/services/upload_finalize.py`.

## CLI

- [x] T024 Implement the `pyfiles` argparse root in `clients/python/src/py_files_cli/__main__.py`, including global `--base-url` resolution.
- [x] T025 Implement `clients/python/src/py_files_cli/commands/login.py` to authenticate against the configured server and store the JWT plus normalized base URL in user config.
- [x] T025a Add CLI tests for base URL normalization, missing `--base-url`, and login config storage.

## Tests And Docs

- [x] T023a Add focused server tests for session create, append, offset mismatch, complete, ownership denial, and size limit behavior.
- [x] T025b Run targeted server and CLI validation, then record exact commands in the closeout.

## Validation

- `cd server && pytest tests/test_upload_sessions.py -vv -s` -> 6 passed, 1 warning.
- `cd clients/python && .venv/bin/python -m pytest tests/test_cli_login.py` -> 3 passed.
