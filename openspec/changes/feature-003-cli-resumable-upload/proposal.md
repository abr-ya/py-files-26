# Feature 003: CLI Resumable Upload

## Summary

Implement a Python CLI upload flow that can run from a user's local machine against a configured py-files server. The CLI shall authenticate with login/password, remember the selected server base URL and access token in local user config, and upload files through resumable upload sessions.

## Motivation

The browser MVP already supports authenticated single-shot uploads. The next deferred milestone is the command-line upload path from `T021`-`T026`, which is required for automation and for large transfers that may need resume after interruption.

## Scope

- Add server upload-session routes for create, append chunk, and complete.
- Add service logic for contiguous chunk writes, received-byte accounting, session state, and final promotion to `StoredUploadObject`.
- Implement the `pyfiles` CLI root, login command, local config storage, and resumable upload command.
- Require an explicit API/server base URL via `--base-url` or saved local config so a local CLI can target a remote server.

## Non-Goals

- Object listing and downloads (`T027`-`T030`) remain feature `004`.
- Google OAuth remains deferred.
- Multi-server profiles and enterprise credential vault integration are out of scope for this slice.

## Traceability

- Backlog item: `003-cli-resumable-upload`
- Source tasks: `T021`-`T026` from `specs/002-network-file-upload-follow-on/tasks.md`
- Existing API contract: `specs/001-network-file-upload-client/contracts/openapi.yaml`
