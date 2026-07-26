# spec-governance Specification

## Purpose
Define repository planning authority after the legacy Spec Kit migration, including OpenSpec source-of-truth rules and legacy traceability.

## Requirements
### Requirement: OpenSpec Source Of Truth

After legacy migration completes, the project MUST treat `openspec/` as the only current source of truth for product requirements, roadmap status, active changes, and archived change history.

#### Scenario: Contributor checks current requirements

- **GIVEN** a contributor needs current product requirements or next work
- **WHEN** the contributor reads repository planning documentation
- **THEN** the contributor is directed to `openspec/specs/`, `openspec/backlog.md`, and active `openspec/changes/`
- **AND** the contributor is not directed to `docs/legacy-specs/` as current authority

### Requirement: Legacy Specs Marker

The project MUST keep legacy Spec Kit material under `docs/legacy-specs/` and mark it as legacy reference material after migration.

#### Scenario: Reader opens legacy specs

- **GIVEN** a reader opens the legacy `docs/legacy-specs/` directory
- **WHEN** the reader looks for current requirements or task status
- **THEN** the directory-level notice identifies the content as legacy
- **AND** the notice points to `openspec/` as the current source of truth

### Requirement: Preserve Legacy Traceability

The project MUST preserve original milestone and task identifiers when migrating source-of-truth status into OpenSpec.

#### Scenario: Follow-on task lookup

- **GIVEN** a future feature references an original task ID such as `T026` or `T030`
- **WHEN** a contributor searches OpenSpec planning artifacts
- **THEN** the contributor can map that task ID to the current OpenSpec backlog or change
- **AND** no duplicate active feature number is used for different work
