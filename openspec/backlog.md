# OpenSpec Backlog

This backlog preserves original task traceability after the project moved from the legacy Spec Kit layout to OpenSpec.

## Sources Of Truth

- Accepted requirements: `openspec/specs/`
- Active feature work: `openspec/changes/`
- Archived feature work: `openspec/changes/archive/`
- Roadmap and feature routing: `openspec/backlog.md`
- Repo-local OpenSpec workflow: `docs/agent-openspec-token-guide.md`
- Legacy reference and original task traceability only: `docs/legacy-specs/`

## Roadmap

| ID | Status | Area | Summary | Source |
| --- | --- | --- | --- | --- |
| 001-network-file-upload-client | Accepted | Browser MVP | FastAPI backend, login/password auth, SQLite metadata, filesystem blob storage, TTL purge hook, multipart browser upload, and vanilla JS upload UI. Original tasks `T001`-`T020` are complete and migrated into accepted OpenSpec capabilities through feature `005`. | `openspec/specs/browser-upload/spec.md`, `openspec/specs/auth-and-accounts/spec.md`, `openspec/specs/stored-objects/spec.md`, `openspec/specs/api-contract/spec.md`, `openspec/specs/spec-governance/spec.md` |
| 002-network-file-upload-follow-on | Backlog | CLI, downloads, parity | Feature `003` accepted tasks `T021`-`T025`; remaining deferred tasks start at `T026`: CLI upload command, object list/download routes and UI, CLI download, OAuth deferred docs, OpenAPI parity, integration tests, TTL denial tests, and quickstart refresh. | `openspec/backlog.md`, active or future `openspec/changes/feature-*` |
| feature-005-migrate-legacy-specs-to-openspec | Accepted | Specs migration | Moved current requirements and roadmap routing to OpenSpec, moved legacy specs to `docs/legacy-specs/`, and kept original task IDs traceable. | `openspec/changes/archive/2026-07-26-feature-005-migrate-legacy-specs-to-openspec/`, `docs/legacy-specs/` |

## Next Candidate Change

`004-cli-resumable-upload-command` remains the active implementation milestone. Keep original task IDs `T021`-`T035` as traceability links when splitting implementation into OpenSpec changes.

Suggested first slice:

- Feature `003` is accepted as server upload sessions plus CLI login/config using tasks `T021`-`T025`.
- Finish feature `004` as the CLI resumable upload command (`T026`).
- Keep list/download work (`T027`-`T030`) as feature `006` unless the implementation needs shared server primitives.
- Leave OAuth and verification polish as feature `007` until explicitly prioritized.

## Deferred Task Groups

### 003 - CLI Auth And Upload Sessions

Accepted server-side resumable upload sessions plus CLI authentication/config for targeting a py-files server from a local machine.

- [x] `T021`: server upload-session routes
- [x] `T022`: chunk append and session state machine
- [x] `T023`: finalize/promote upload session
- [x] `T024`: CLI argparse entry
- [x] `T025`: CLI login and JWT storage

### 004 - CLI Resumable Upload Command

CLI upload command for local-machine file transfers using the saved server URL/token and resumable upload sessions.

- `T026`: resumable upload driver

### 005 - Legacy Specs To OpenSpec Migration

Accepted docs/spec migration that makes `openspec/` the only current source of truth and moves legacy specs to `docs/legacy-specs/`.

- Migrate accepted behavior into capability-oriented OpenSpec specs
- Preserve original task IDs `T001`-`T035` as traceability links
- Move legacy specs under `docs/legacy-specs/` and update OpenSpec-first workflow guidance

### 006 - List And Download

- `T027`: object listing route
- `T028`: object metadata and content download routes
- `T029`: browser object list and download UI
- `T030`: CLI download command

### 007 - Docs And Verification Polish

- `T031`: document OAuth as deferred
- `T032`: reconcile OpenAPI parity
- `T033`: login/upload/list/download integration test
- `T034`: TTL denial test
- `T035`: quickstart refresh

## Working Rules

- Do not renumber the existing `001` and `002` milestones.
- Do not mark `002` accepted until the deferred Variant C work is implemented and verified.
- Number new OpenSpec changes sequentially (`003`, `004`, `005`, ...), without letter suffixes.
- Treat `docs/legacy-specs/` as legacy reference only; use it only for historical context and original task traceability.
- For future OpenSpec changes, create `openspec/changes/<change-id>/` artifacts first, then archive only after validation and accepted spec sync.
