# Feature 004: CLI Resumable Upload Command

## Summary

Implement `pyfiles upload <path>` using the saved server URL/token from feature `003` and the resumable upload-session API. The command shall create an upload session, append file chunks with contiguous `Upload-Offset` values, complete the session, and preserve retry metadata for interrupted uploads.

## Motivation

Feature `003` established server upload-session primitives and CLI login/config. The next useful CLI increment is actual file transfer from a local machine while keeping list/download work separate.

## Scope

- Implement `clients/python/src/py_files_cli/commands/upload.py`.
- Resolve base URL and token from explicit `--base-url` or saved local config.
- Create, append, and complete upload sessions through `/api/v1/upload-sessions`.
- Preserve local retry metadata so an interrupted upload can resume when the local file still matches the saved metadata.
- Add focused CLI tests for missing config, saved config reuse, upload flow, and resume behavior.

## Non-Goals

- Object listing and downloads remain feature `006` after the legacy specs migration.
- Browser UI changes are out of scope.
- Multi-server profiles and external credential vaults are out of scope.

## Traceability

- Backlog item: `004-cli-resumable-upload-command`
- Source task: `T026`, preserved through `openspec/backlog.md` traceability from the legacy follow-on tracker
- Depends on feature `003-cli-auth-upload-sessions`
