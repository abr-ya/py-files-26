# Tasks: Feature 004 CLI Resumable Upload Command

## CLI

- [ ] T026 Implement `clients/python/src/py_files_cli/commands/upload.py` with resumable upload-session create/append/complete flow, progress output, interruption-safe retry metadata, and clear exit codes.
- [ ] T026d Implement `pyfiles status` as a lightweight remote server preflight that resolves explicit or saved base URL, checks `GET /health`, prints a concise result, and returns clear exit codes without requiring token validation.

## Tests And Docs

- [ ] T026a Add CLI tests for missing base URL/token, explicit `--base-url`, saved config reuse, login storage reuse, status preflight success/failure, resumable upload happy path, offset mismatch handling, and retry behavior.
- [ ] T026b Update `clients/python/README.md` with runnable CLI status and upload examples using `--base-url`; update any current OpenSpec-routed docs instead of relying on `docs/legacy-specs/` as source of truth.
- [ ] T026c Run targeted CLI validation and local smoke validation, then record exact commands in the closeout.
