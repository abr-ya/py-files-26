## Why

The repository currently has two competing specification homes: accepted OpenSpec material lives under `openspec/`, while the original product specification, data model, OpenAPI contract, quickstart, and follow-on task tracker still live under `specs/`. This change makes `openspec/` the single source of truth and marks the old `specs/` tree as legacy reference material so future work starts from one planning surface.

## What Changes

- Migrate accepted behavior from `specs/001-network-file-upload-client/` into capability-oriented OpenSpec specs.
- Migrate deferred follow-on scope from `specs/002-network-file-upload-follow-on/` into OpenSpec backlog/change-ready routing without losing original task IDs `T021`-`T035`.
- Keep `openspec/specs/cli-resumable-upload/spec.md` as the accepted Feature 003 capability and avoid duplicating it.
- Add a clear legacy notice to the root `specs/` tree that points readers to `openspec/` as the current source of truth.
- Update `openspec/backlog.md` so feature `005` is this migration and the previously listed List/Download work moves to the next available feature number.
- No runtime code, API behavior, storage behavior, or CLI behavior changes.

## Capabilities

### New Capabilities

- `browser-upload`: accepted browser MVP behavior for login/password access, authenticated single-shot upload, upload outcomes, and retry guidance.
- `auth-and-accounts`: accepted authentication, JWT/session, account provisioning, and deferred OAuth behavior.
- `stored-objects`: accepted stored object model, ownership, retention, list/download requirements, and follow-on implementation status.
- `api-contract`: accepted API contract governance for `/api/v1`, JSON metadata, binary transfer surfaces, and OpenAPI ownership.
- `spec-governance`: rules that make `openspec/` the current source of truth and mark `specs/` as legacy reference after migration.

### Modified Capabilities

- None. `cli-resumable-upload` remains the accepted Feature 003 capability; this change may update references to it but does not change its requirements.

## Impact

- Affects OpenSpec artifacts under `openspec/specs/`, `openspec/backlog.md`, and this change directory.
- Affects legacy documentation under `specs/` by adding an explicit legacy/source-of-truth notice and, if needed, lightweight pointers to OpenSpec.
- Affects repo workflow documentation only if it still names legacy `specs/` as a source of truth.
- Does not affect `server/`, `frontend/`, or `clients/python/` runtime code.
