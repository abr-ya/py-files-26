# Feature Specification: Network File Upload Client

**Feature Branch**: `001-network-file-upload-client`  
**Created**: 2026-04-29  
**Status**: Accepted — incremental delivery (Phase 3 browser MVP shipped in repo; remaining stories deferred — see [`tasks.md`](./tasks.md), [`specs/002-network-file-upload-follow-on/`](../002-network-file-upload-follow-on/spec.md))

**Input**: User description: "We are building a client for sending files over the network—via a browser or a Python script, from the command line or with a UI. The frontend and backend may be implemented in one or more languages. Authentication should be simple: login plus password is sufficient; Google accounts may be added optionally."

## Clarifications

### Increment scope (repository milestone)

This merge closes **Phase 3** (**User Story 1** — browser upload). Stories **2–4** and tasks **`T021`–`T035`** move to **`specs/002-network-file-upload-follow-on/`**. Until that work ships, **Variant C** (download round-trip + CLI resume) from the Q&A below is **not** fully satisfied—only browser upload is in scope.

### Session 2026-04-29

- Q: What is in scope for the MVP after upload (upload only, listing, download)? → A: **Variant C** — upload **and** the ability to **download files previously uploaded by the same user** (web and CLI).
- Q: Maximum single-file size in the MVP? → A: **Variant B** — **no more than 1 GB** per object (upload and delivery).
- Q: How are accounts provisioned? → A: **Variant C (recommended)** — hybrid: self-service registration and/or operator-created accounts are controlled by **environment configuration**.
- Q: Resume / chunked upload in the MVP? → A: **Variant C** — resume is **mandatory for the CLI**; for the **browser**, resumable upload is **not mandatory** in the MVP (full retry with a clear message is sufficient).
- Q: Retention policy for uploaded files? → A: **Variant B** — default auto-deletion **30 days** after upload; the period is configurable via deployment settings.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Authenticated upload from the browser (Priority: P1)

The user opens the web application, signs in with login and password, and sends one or more files to the server; after completion they see success or an understandable error.

**Why this priority**: the product’s primary value is delivering files through a familiar browser UI without installing a separate client.

**Independent Test**: exercise the browser path only: sign in as a test user, upload a file of fixed size, verify success confirmation on screen.

**Acceptance Scenarios**:

1. **Given** the user is not authenticated, **When** they enter a valid login and password and submit the sign-in form, **Then** the system allows them to upload files.
2. **Given** the user is authenticated, **When** they select a file and confirm upload, **Then** the system accepts the file and reports successful completion or the reason for failure.
3. **Given** the user is authenticated, **When** they upload several files in one session, **Then** each file gets an explicit outcome (success or error with cause).

---

### User Story 2 - Authenticated upload from a command-line client (Priority: P2)

The user runs a console client on their machine, supplies credentials (or uses a persisted session if supported), points to file(s), and receives a terminal result and exit code suitable for automation.

**Why this priority**: CI/CD and power-user flows need a path without a UI; it broadens reach without requiring every user to do web development.

**Independent Test**: CLI only: configure a test user, run a single-file upload command, verify stdout/stderr and exit code without launching a browser.

**Acceptance Scenarios**:

1. **Given** the console client is installed and credentials are known, **When** the user starts an upload for the specified file, **Then** the operation ends with a success message or a diagnosable error.
2. **Given** credentials are wrong, **When** the user starts an upload, **Then** the client reports authentication failure without treating file content as accepted.
3. **Given** upload of a file up to 1 GB was interrupted mid-transfer, **When** the user retries with the supported resume flow, **Then** the operation succeeds without requiring a full resend of bytes already accepted (clarification variant C, 2026-04-29).

---

### User Story 3 - Download previously uploaded files (Priority: P2)

After a successful upload, the user can locate their file and download it via the browser or the console client; access is limited to objects uploaded by that user.

**Why this priority**: without returning the file to the user, **Variant C** is not satisfied (not just “fire and forget”).

**Independent Test**: upload a file, then run download scenarios only (no new upload in the same run)—verify integrity and access control.

**Acceptance Scenarios**:

1. **Given** the user previously uploaded a file successfully and is authenticated, **When** they request download of that file through the web UI, **Then** the browser receives the data stream and save completes without error, or a clear denial reason is shown.
2. **Given** the same context, **When** the user runs a download command in the CLI with the same credentials, **Then** the file is saved locally or the stream ends with a diagnosable error code.
3. **Given** another user (or no session), **When** they attempt to download an object uploaded by someone else, **Then** access is denied and the message does not reveal other users’ files or contents.
4. **Given** the object was removed by the server after the retention period (TTL policy), **When** the owner requests download, **Then** the operation fails with a clear explanation and no hint at content (clarification variant B, 2026-04-29).

---

### User Story 4 - Optional sign-in with Google (Priority: P3)

The user may sign in with a Google account instead of login plus password if an administrator enables this option.

**Why this priority**: it reduces friction for Google users but does not block the MVP on OAuth integrations.

**Independent Test**: with the option enabled—sign in with Google on a test environment and complete one successful upload; with it disabled—the flow is unavailable and this is documented.

**Acceptance Scenarios**:

1. **Given** Google sign-in is enabled, **When** the user chooses Google and completes the provider flow, **Then** they reach the same “can upload files” state as after password sign-in.

---

### Edge Cases

- File **larger than 1 GB** or exceeding deployment policy—reject before ingest completes when possible; otherwise a clear error and abort without false success; if the server disk is full—a clear message without hanging.
- Network interruption during transfer—the client reports failure. **CLI**: MUST support resuming uploads up to **1 GB** in the MVP (clarification variant C). **Browser**: MAY rely on repeating a full upload with a clear message, without mandatory resumable upload in the MVP.
- Concurrent uploads from one user—results are not mixed up; for the CLI, exit codes MUST be predictable for batch operations (document batch behavior).
- Credentials MUST NOT be sent in plaintext over the network in the MVP (protected transport expected).
- Download: object missing or unavailable on the server—the user gets a clear error; identifier guessing MUST not leak metadata about other objects.
- **TTL** expiry: after deletion under retention policy, a download attempt MUST yield an explainable denial (clarification variant B, 2026-04-29).
- **Registration disabled** mode: a user without an account cannot self-provision via an exposed signup path; the message SHOULD direct them to an operator without exposing internal rules.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide login-password authentication for access to file uploads.
- **FR-002**: The system MUST provide a web UI for selecting and uploading files after successful authentication and for requesting download of the user’s previously accepted objects (minimal object-selection UX—as defined in the plan).
- **FR-003**: The system MUST provide a console client for sending files using the same credentials (or an equivalent secure flow), suitable for automation scenarios.
- **FR-004**: The system MUST show or print progress for long-running transfers and a final outcome (success, cancellation, or error with reason).
- **FR-005**: The system MUST reject upload on failed authentication and MUST NOT acknowledge receipt if the server rejects the upload.
- **FR-006**: The system MAY support Google sign-in for the same upload and download flows; if not shipped, behavior MUST be documented as unavailable without breaking User Stories 1–3.
- **FR-007**: After a successful upload, the system MUST allow the same user to download that object via the web UI and the console client when authenticated.
- **FR-008**: The system MUST forbid downloading objects uploaded by another user and MUST NOT reveal existence or attributes of others’ objects on denial.
- **FR-009**: In the MVP, a single uploaded object MUST be **no larger than 1 GB**; the system MUST reject oversized files with a clear message (ideally before ingest or without completing full-body acceptance; protocol details—in the plan). Stored and delivered objects MUST not exceed this limit by design.
- **FR-010**: The system MUST support a configurable account-provisioning mode (clarification variant C, 2026-04-29): either self-service registration is available, or new accounts are created only by an operator/administrator (or equivalent managed process). The active mode MUST be documented per environment; if registration is disabled, the user MUST see a clear explanation instead of a silent denial.
- **FR-011**: In the MVP, the console client MUST support resuming or an equivalent chunked upload after interruption for objects up to **1 GB**; the server MUST expose a compatible contract (details—in the plan). The web client MAY omit resume in the MVP if the user gets clear guidance to **retry the full upload** after failure (clarification variant C, 2026-04-29).
- **FR-012**: The system MUST delete stored objects after their retention period from successful server acceptance; the default is **30 calendar days** unless deployment configuration states otherwise (clarification variant B, 2026-04-29). Download attempts after deletion MUST get a clear message; where it does not overload the primary flow, the MVP SHOULD surface the applicable period or policy to the user.

### Key Entities

- **User**: account with login identifier and password secret; optional link to an external provider (Google).
- **Registration policy (deployment configuration)**: defines whether self-service registration is allowed or only operator-provisioned accounts (Variant C).
- **Session / access token**: represents successful authentication without resending the password on every request (details at design time).
- **File in transit**: name, size, data stream; server-side acceptance outcome.
- **Stored upload object**: owned by the user; has a stable identifier for later download under the MVP access policy (Variant C); stored size does not exceed **1 GB** in the MVP (clarification variant B, 2026-04-29); subject to deletion when the storage TTL expires (clarification variant B, 2026-04-29).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: At least 90% of controlled test uploads (typical file up to 100 MB on a stable network) complete successfully with user-visible confirmation when credentials are valid.
- **SC-002**: In a typical scenario (one file up to 100 MB, stable network), the user receives a final success or error status within 5 seconds after the transfer ends.
- **SC-003**: At least 95% of usability-test participants (≥5 people) complete their first browser upload on the first or second try without consulting documentation.
- **SC-004**: The “upload one file” console scenario can be repeated by a script and yields a reproducible exit code (success / known error) on 100% of runs on the reference environment.
- **SC-005**: In the controlled test “upload typical file up to 100 MB → download as the same user,” at least 95% of runs show a reproducible size match (checksum match at plan time if checksums are defined).
- **SC-006**: In a controlled interruption during **CLI** upload (file up to 1 GB), at least 90% of retries with resume complete acceptance without resending the full object (metric captured on the reference environment and in the plan).
- **SC-007**: With the default **30-day** TTL configuration, all controlled download attempts after a simulated expiry end in denial with clear text and without revealing content (100% of reference runs).

## Assumptions

- The reference console client is Python with cross-platform support for Windows, Linux, and macOS per the repository constitution; other languages remain allowed for the server or alternate clients while user-facing scenarios hold.
- Frontend and backend may use different languages; the spec does not fix the stack but expects explicit contracts in the plan.
- The **per-object** upper bound in the MVP is fixed by clarification **variant B**: **up to 1 GB inclusive**; per-user or deployment-wide quotas may be set in the plan.
- Google sign-in is treated as an optional extension after login-password works end-to-end.
- MVP data scope includes the **full upload-and-download cycle for one’s own file** (clarification variant C, 2026-04-29); a “list only, no download” mode is not required.
- Account provisioning is **configuration hybrid** (clarification variant C, 2026-04-29): the concrete mode per installation is set at deploy time and validated via sign-in/registration scenarios.
- Resume policy (clarification variant C, 2026-04-29): resumable upload is mandatory for the **CLI**; optional for the **browser** in the MVP.
- Storage policy (clarification variant B, 2026-04-29): default TTL **30 days**, overridden by deployment configuration.
