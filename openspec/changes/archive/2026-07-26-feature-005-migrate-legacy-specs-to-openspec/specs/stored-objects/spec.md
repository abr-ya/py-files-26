## ADDED Requirements

### Requirement: Stored Object Ownership

The system MUST store accepted upload metadata as user-owned objects and enforce ownership for later object access.

#### Scenario: Stored object created for owner

- **GIVEN** an authenticated upload is accepted
- **WHEN** the server persists the upload metadata
- **THEN** the stored object records the owning user
- **AND** later object access is scoped to that owner

#### Scenario: Cross-user object access denied

- **GIVEN** an object belongs to one user
- **WHEN** a different user requests that object's metadata or content
- **THEN** the system denies access
- **AND** the denial does not reveal the object's private metadata or content

### Requirement: Stored Object Size And Checksum Metadata

The system MUST record stored object metadata needed for user-visible names, size limits, storage lookup, and integrity verification.

#### Scenario: Accepted object metadata

- **GIVEN** an upload is accepted into storage
- **WHEN** the object metadata is persisted
- **THEN** the metadata includes a stable identifier, owner, original filename, byte size, storage location, and acceptance timestamp
- **AND** the byte size does not exceed the configured maximum object size

### Requirement: Retention And Expiry

The system MUST apply a configurable retention period to stored objects and deny access after expiry.

#### Scenario: Expired object download

- **GIVEN** a stored object has expired under the configured retention policy
- **WHEN** the owner requests the object content
- **THEN** the system denies the request with a clear explanation
- **AND** no object content is returned

### Requirement: List And Download Roadmap Routing

The system MUST track object listing and download implementation as deferred follow-on work until the relevant routes, browser UI, and CLI command are completed.

#### Scenario: Deferred list and download work

- **GIVEN** object list and download tasks remain incomplete
- **WHEN** future planning resumes that area
- **THEN** the work is routed through OpenSpec backlog and a future OpenSpec change
- **AND** original task IDs `T027` through `T030` remain traceable
