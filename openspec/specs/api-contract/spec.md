# api-contract Specification

## Purpose
Define API contract governance for versioned py-files HTTP APIs, metadata formats, binary transfers, and OpenAPI routing.

## Requirements
### Requirement: Versioned API Contract

The system MUST define authenticated file API behavior under the versioned `/api/v1` contract surface.

#### Scenario: API route governance

- **GIVEN** an API endpoint is added or changed for auth, objects, or upload sessions
- **WHEN** the behavior becomes part of accepted project scope
- **THEN** the accepted OpenSpec capability describes the requirement
- **AND** the OpenAPI contract is updated or explicitly identified as deferred parity work

### Requirement: Metadata And Binary Transfer Formats

The API contract MUST distinguish JSON metadata operations from binary file transfer operations.

#### Scenario: Object metadata and content formats

- **GIVEN** a client interacts with stored objects
- **WHEN** the client requests metadata
- **THEN** the API returns JSON metadata
- **AND** when the client requests file content, the API returns an octet-stream binary response

### Requirement: OpenAPI Source Routing

The project MUST route OpenAPI contract authority through OpenSpec after legacy migration completes.

#### Scenario: OpenAPI referenced after migration

- **GIVEN** a contributor needs the current API contract
- **WHEN** the contributor starts from repository documentation
- **THEN** the contributor is directed to the OpenSpec source-of-truth location
- **AND** any legacy OpenAPI copy is marked historical or reference-only
