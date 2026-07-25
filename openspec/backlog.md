# OpenSpec Backlog

This backlog preserves the existing specification numbering while the project moves from the original `specs/` layout toward OpenSpec.

## Sources Of Truth

- Accepted MVP increment: `specs/001-network-file-upload-client/`
- Deferred follow-on increment: `specs/002-network-file-upload-follow-on/`
- Repo-local OpenSpec workflow: `docs/agent-openspec-token-guide.md`

## Roadmap

| ID | Status | Area | Summary | Source |
| --- | --- | --- | --- | --- |
| 001-network-file-upload-client | Accepted | Browser MVP | FastAPI backend, login/password auth, SQLite metadata, filesystem blob storage, TTL purge hook, multipart browser upload, and vanilla JS upload UI. Tasks `T001`-`T020` are complete. | `specs/001-network-file-upload-client/spec.md`, `specs/001-network-file-upload-client/tasks.md` |
| 002-network-file-upload-follow-on | Backlog | CLI, downloads, parity | Deferred tasks `T021`-`T035`: resumable CLI upload, object list/download routes and UI, CLI download, OAuth deferred docs, OpenAPI parity, integration tests, TTL denial tests, and quickstart refresh. | `specs/002-network-file-upload-follow-on/spec.md`, `specs/002-network-file-upload-follow-on/tasks.md` |

## Next Candidate Change

`003-cli-auth-upload-sessions` is the current feature milestone. Keep original task IDs `T021`-`T035` as traceability links when splitting implementation into OpenSpec changes.

Suggested first slice:

- Finish `003` as server upload sessions plus CLI login/config using tasks `T021`-`T025`.
- Move the CLI resumable upload command (`T026`) into feature `004`.
- Keep list/download work (`T027`-`T030`) as feature `005` unless the implementation needs shared server primitives.
- Leave OAuth as docs-only feature `006` until explicitly prioritized.

## Deferred Task Groups

### 003 - CLI Auth And Upload Sessions

Server-side resumable upload sessions plus CLI authentication/config for targeting a py-files server from a local machine.

- `T021`: server upload-session routes
- `T022`: chunk append and session state machine
- `T023`: finalize/promote upload session
- `T024`: CLI argparse entry
- `T025`: CLI login and JWT storage

### 004 - CLI Resumable Upload Command

CLI upload command for local-machine file transfers using the saved server URL/token and resumable upload sessions.

- `T026`: resumable upload driver

### 005 - List And Download

- `T027`: object listing route
- `T028`: object metadata and content download routes
- `T029`: browser object list and download UI
- `T030`: CLI download command

### 006 - Docs And Verification Polish

- `T031`: document OAuth as deferred
- `T032`: reconcile OpenAPI parity
- `T033`: login/upload/list/download integration test
- `T034`: TTL denial test
- `T035`: quickstart refresh

## Working Rules

- Do not renumber the existing `001` and `002` milestones.
- Do not mark `002` accepted until the deferred Variant C work is implemented and verified.
- Number new OpenSpec changes sequentially (`003`, `004`, `005`, ...), without letter suffixes.
- For future OpenSpec changes, create `openspec/changes/<change-id>/` artifacts first, then archive only after validation and accepted spec sync.
