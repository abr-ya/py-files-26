# Feature 003: CLI Auth And Upload Sessions

## Summary

Implement the server-side resumable upload-session protocol and the Python CLI authentication/config foundation. The CLI shall authenticate with login/password, remember the selected server base URL and access token in local user config, and leave the actual CLI file upload driver for the next feature.

## Motivation

The browser MVP already supports authenticated single-shot uploads. The next deferred milestone needs server upload-session primitives before the CLI can upload large files safely. Splitting the CLI upload driver keeps this feature small while still producing a usable CLI login/config increment.

## Scope

- Add server upload-session routes for create, append chunk, and complete.
- Add service logic for contiguous chunk writes, received-byte accounting, session state, and final promotion to `StoredUploadObject`.
- Implement the `pyfiles` CLI root, login command, and local config storage.
- Require an explicit API/server base URL via `--base-url` or saved local config so a local CLI can target a remote server.

## Non-Goals

- CLI upload command and resumable retry metadata (`T026`) move to feature `004`.
- Object listing and downloads (`T027`-`T030`) remain feature `005`.
- Google OAuth remains deferred.
- Multi-server profiles and enterprise credential vault integration are out of scope for this slice.

## Traceability

- Backlog item: `003-cli-auth-upload-sessions`
- Source tasks: `T021`-`T025` from `specs/002-network-file-upload-follow-on/tasks.md`
- Existing API contract: `specs/001-network-file-upload-client/contracts/openapi.yaml`
