# Tasks: Feature 004 CLI Resumable Upload Command

## CLI

- [ ] T026 Implement `clients/python/src/py_files_cli/commands/upload.py` with resumable upload-session create/append/complete flow, progress output, interruption-safe retry metadata, and clear exit codes.

## Tests And Docs

- [ ] T026a Add CLI tests for missing base URL/token, explicit `--base-url`, saved config reuse, login storage reuse, resumable upload happy path, offset mismatch handling, and retry behavior.
- [ ] T026b Update `clients/python/README.md` and `specs/001-network-file-upload-client/quickstart.md` with runnable CLI upload examples using `--base-url`.
- [ ] T026c Run targeted CLI validation and local smoke validation, then record exact commands in the closeout.

