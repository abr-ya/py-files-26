<!--
Sync Impact Report (speckit-constitution)
- Version change: 1.0.0 → 1.0.1
- Change type: Editorial — unified formatting and normative wording across principles; no policy intent change
- Modified principles: style normalization only (headings, MUST/SHOULD, paragraph structure for former bullet lists)
- Templates requiring updates: none for this edit
- Follow-up TODOs: none
-->

# py-files-26 Constitution

## Core Principles

### 1. Spec-kit workflow fidelity

Features MUST follow the Specify workflows (`/speckit.specify`, clarification as needed,
`/speckit.plan`, `/speckit.tasks`, `/speckit.implement`) unless the feature brief explicitly
documents a waived path (for example a spike). Specification artifacts MUST live under the
feature’s designated `specs/` paths and remain the source of truth for scope.

### 2. Constitution authority (NON-NEGOTIABLE)

`.specify/memory/constitution.md` overrides ad hoc conventions: `spec.md`, `plan.md`, and
`tasks.md` MUST NOT contradict it. Conflicts MUST be resolved by revising those artifacts or by
running `/speckit-constitution` to amend governance deliberately—not by silently ignoring a MUST.

### 3. Independent, testable increments

User scenarios MUST be prioritized (P1, P2, …) and independently testable. Acceptance criteria
MUST be concrete enough to verify without subjective interpretation.

### 4. Verification discipline

Implementations MUST include automated verification where the stack supports it (unit tests,
contract checks, linters). If automated checks are omitted, the omission MUST be justified in the
feature plan’s Complexity Tracking (or equivalent) with an explicit mitigation.

### 5. Security first

Passwords MUST NOT be transmitted in plaintext—only hashes or tokens as appropriate. All file
operations MUST be logged on the client without logging file contents. Authentication MUST be
required for every operation except a documented public download, when that mode exists.

### 6. Client cross-platform compatibility

The Python client MUST run on Windows, Linux, and macOS without platform-specific patches. Any
browser client MUST support current versions of Chrome, Firefox, Edge, and Safari (last two major
versions each).

### 7. Explicit client–server contract

The API MUST be REST-shaped with JSON for metadata and binary streams for file payloads. URLs MUST
include explicit versioning (for example `/api/v1/...`). Every endpoint MUST be described in an
OpenAPI (YAML) document kept with the project.

### 8. Simplicity as competitive advantage

Dependencies MUST stay minimal: the Python client SHOULD rely on `requests`, `typing`, and the
standard library unless the plan documents a broader exception. Browser clients SHOULD use vanilla
JavaScript or a lightweight layer; React, Vue, or similar frameworks MUST NOT be introduced unless
the feature plan documents why and addresses trade-offs (for example under Complexity Tracking). A
graphical UI for the Python client is optional where a CLI satisfies the scenario.

### 9. Testability out of the box

Authentication, upload, file listing, and comparable surfaces MUST each have automated tests.
External calls MUST be exercised with mocks or test doubles so suites run without live services.

### 10. Transparent operation status

Users MUST always receive clear feedback for long-running actions: upload progress, success or
failure, and actionable error reasons when something goes wrong.

## Technology & Repository Constraints

Default stack assumption for work in this repository is Python unless a feature plan explicitly
defines another primary language or runtime. Dependencies and deployment constraints MUST be stated
in `plan.md` for each feature so reviewers can validate Principle IV.

## Workflow & Quality Gates

Plans MUST complete the Constitution Check before Phase 0 research and re-check after Phase 1
design. Before implementation, `/speckit.analyze` SHOULD run when `tasks.md` exists to validate
alignment across spec, plan, and tasks.

## Governance

Amendments MUST update `.specify/memory/constitution.md` via `/speckit-constitution` (or an
explicit documented equivalent), bump `CONSTITUTION_VERSION` per semantic versioning (MAJOR:
backward-incompatible governance; MINOR: new principles or material guidance; PATCH: clarifications
only), and record ratification/amendment dates. Compliance SHOULD be verified during planning,
`/speckit.analyze`, and review—not only at merge time.

**Version**: 1.0.1 | **Ratified**: 2026-04-29 | **Last Amended**: 2026-04-29
