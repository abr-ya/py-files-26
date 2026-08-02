# Tasks: Feature 004 CLI Resumable Upload Command

## CLI

- [x] T026 Implement `clients/python/src/py_files_cli/commands/upload.py` with resumable upload-session create/append/complete flow, progress output, interruption-safe retry metadata, and clear exit codes.
- [x] T026d Implement `pyfiles status` as a lightweight remote server preflight that resolves explicit or saved base URL, checks `GET /health`, prints a concise result, and returns clear exit codes without requiring token validation.

## Tests And Docs

- [x] T026a Add CLI tests for missing base URL/token, explicit `--base-url`, saved config reuse, login storage reuse, status preflight success/failure, resumable upload happy path, offset mismatch handling, and retry behavior.
- [x] T026b Update `clients/python/README.md` with runnable CLI status and upload examples using `--base-url`; update any current OpenSpec-routed docs instead of relying on `docs/legacy-specs/` as source of truth.
- [x] T026c Run targeted CLI validation and local smoke validation, then record exact commands in the closeout.

Validation evidence:

- `server/.venv/bin/pytest tests/test_health.py`: 1 passed, 1 warning.
- `server/.venv/bin/pytest tests/test_upload_sessions.py`: 6 passed, 1 warning.
- `clients/python/.venv/bin/pytest tests`: 13 passed.
- `clients/python/.venv/bin/pytest tests/test_cli_upload.py`: 6 passed.
- `clients/python/.venv/bin/pyfiles --base-url http://127.0.0.1:8000 status`: `ok: http://127.0.0.1:8000`.
- `clients/python/.venv/bin/pyfiles upload /tmp/pyfiles-smoke.txt`: uploaded 13/13 bytes and returned object id `de74c629-3495-46c1-a049-0cc825fbc8ad`.
