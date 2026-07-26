## Context

The project started with Spec Kit artifacts under `specs/001-network-file-upload-client/` and `specs/002-network-file-upload-follow-on/`. OpenSpec was introduced later, and Feature 003 has already produced an accepted OpenSpec capability at `openspec/specs/cli-resumable-upload/spec.md`.

The result is a split planning surface:

- `openspec/` contains active changes, archived changes, backlog, and one accepted capability.
- `specs/` still contains the original product spec, data model, OpenAPI contract, quickstart, and follow-on task list.
- Future agents can accidentally treat the legacy `specs/` tree as current authority even after OpenSpec adoption.

This feature is a documentation and planning migration. It does not change runtime behavior.

## Goals / Non-Goals

**Goals:**

- Make `openspec/` the only current source of truth after this feature is archived.
- Preserve the original product decisions from `specs/001-network-file-upload-client/`.
- Preserve follow-on traceability for tasks `T021`-`T035`.
- Mark `specs/` clearly as legacy reference so it stops steering new planning.
- Keep Feature 004 active and keep CLI upload implementation scope separate.
- Renumber the next List/Download work because feature number `005` is now this migration.

**Non-Goals:**

- No server, frontend, or CLI implementation changes.
- No OpenAPI behavior changes.
- No attempt to finish `T026`-`T035`.
- No deletion of the legacy `specs/` tree in this feature.

## Decisions

### Capability-oriented OpenSpec layout

Create several small accepted capability specs instead of one large migrated monolith:

- `browser-upload`
- `auth-and-accounts`
- `stored-objects`
- `api-contract`
- `spec-governance`

Rationale: OpenSpec specs are easier to sync and archive when each capability has focused requirements. This also lets later features modify only the relevant capability.

Alternative considered: migrate `specs/001-network-file-upload-client/spec.md` into one `network-file-upload-client` OpenSpec spec. That would preserve the old shape but keep unrelated auth, browser, storage, API, and governance rules bundled together.

### Keep legacy files, add explicit legacy marker

Do not move or delete the old `specs/` tree yet. Add a root legacy notice that tells readers `openspec/` is authoritative and `specs/` is historical reference.

Rationale: deleting the old files would make review noisier and risks losing useful context such as the original Q&A, research notes, and quickstart examples. A visible notice solves the source-of-truth problem without destructive churn.

Alternative considered: move `specs/` to `docs/archive/specs/`. That may be a future cleanup, but it is not necessary to make OpenSpec authoritative.

### Treat deferred work as backlog, not accepted implementation

OpenSpec should preserve the product intent for list/download, OAuth, OpenAPI parity, and verification polish, but unfinished tasks remain in `openspec/backlog.md` and future changes.

Rationale: accepted specs should not imply that deferred behavior is already implemented. This keeps product truth and implementation status separate.

Alternative considered: migrate every old FR as accepted behavior regardless of implementation status. That would recreate the old ambiguity in a new folder.

### Renumber pending roadmap rows

Feature `005` is this migration. The previously listed List/Download group should move to the next available number, with Docs/Verification Polish moving after it.

Rationale: two different feature 005 meanings would make future status questions and branches confusing.

Alternative considered: use a letter suffix like `004-a`. The repo working rules currently say new OpenSpec changes should use sequential numbers without letter suffixes.

## Risks / Trade-offs

- Old and new specs may briefly overlap during implementation -> keep this feature docs-only and archive it before starting more implementation work.
- Requirements may become too broad during migration -> split into capability specs and keep tasks focused on migration, notices, and validation.
- Deferred behavior may be accidentally marked implemented -> keep `T026`-`T035` unchecked and route them through future feature numbers.
- The OpenAPI contract may remain physically under `specs/` -> either move it into `openspec/specs/api-contract/` during implementation or leave a clearly named legacy copy with OpenSpec pointing to the authoritative location.

## Migration Plan

1. Add OpenSpec capability specs for accepted browser upload, auth/accounts, stored objects, API contract governance, and spec governance.
2. Update `openspec/backlog.md` so `openspec/` is listed as the source of truth and feature numbers remain unique.
3. Add a visible legacy notice under `specs/`, pointing to the OpenSpec locations.
4. Update repo workflow docs if they still name `specs/` as live source of truth.
5. Run `openspec validate --specs --strict`, `openspec validate --changes --strict`, and `git diff --check`.

Rollback is a docs-only revert: remove the new OpenSpec specs/change artifacts and restore previous backlog/source-of-truth wording.

## Source Mapping

| Legacy source | Classification | OpenSpec destination |
| --- | --- | --- |
| `specs/001-network-file-upload-client/spec.md` | Product requirements, scenarios, edge cases, success criteria | Split across `browser-upload`, `auth-and-accounts`, `stored-objects`, `api-contract`, and existing `cli-resumable-upload` |
| `specs/001-network-file-upload-client/plan.md` | Architecture and implementation notes | Summarize only stable governance points in `api-contract`; keep detailed stack notes as legacy reference |
| `specs/001-network-file-upload-client/data-model.md` | Product data model and validation notes | `stored-objects`, `auth-and-accounts`, and existing `cli-resumable-upload` |
| `specs/001-network-file-upload-client/contracts/openapi.yaml` | API contract artifact | Route authority through `api-contract`; keep or move the YAML according to implementation review, but legacy copies must not be treated as current unless referenced by OpenSpec |
| `specs/001-network-file-upload-client/quickstart.md` | Operational quickstart | Legacy reference unless refreshed by future docs/verification work |
| `specs/001-network-file-upload-client/research.md` | Historical decision record | Legacy reference; migrate only decisions needed by current capability specs |
| `specs/001-network-file-upload-client/tasks.md` | Completed original task tracker `T001`-`T020` | Traceability reference; accepted behavior moves to OpenSpec specs |
| `specs/001-network-file-upload-client/checklists/requirements.md` | Historical review checklist | Legacy reference |
| `specs/002-network-file-upload-follow-on/spec.md` | Deferred follow-on milestone wrapper | OpenSpec backlog routing and future changes |
| `specs/002-network-file-upload-follow-on/tasks.md` | Follow-on task tracker `T021`-`T035` | `openspec/backlog.md` with original task IDs preserved; completed `T021`-`T025` remain covered by `cli-resumable-upload` |

Feature 003 accepted behavior already lives in `openspec/specs/cli-resumable-upload/spec.md`; this migration should reference that spec instead of copying its requirements into new capability specs.
