# Feature Specification: Network File Upload Client — Deferred Milestones (Follow-On)

**Feature Branch**: `002-network-file-upload-follow-on`  
**Created**: 2026-04-29 · **Specification completed**: 2026-04-30  
**Status**: Accepted for planning  

**Prerequisite**: [`specs/001-network-file-upload-client/`](../001-network-file-upload-client/) — phased delivery through **authenticated browser upload** (User Story 1) is merged; clarified product outcome **includes** retrieval of one’s own files and interruption-tolerant uploads for scripted clients (see Clarifications and Success Criteria below).

**Input**: «Мы отложили часть фаз и задач в первой фиче. Давай все их возьмем в работу сейчас.» — i.e., bring into active scope everything previously deferred beyond the browser MVP boundary: scripted upload with interruption recovery; listing and download of the authenticated user’s own stored items; documenting optional third‑party identity where not implemented; and closing verification/consistency gaps for the negotiated contract against behavior.

---

## Clarifications *(scope bridge from parent feature)*

- **Inclusive scope**: This milestone satisfies the remaining outcomes that were postponed from **`001`** (browser-only slice). **Operational delivery** MUST cover scripted **interruption‑tolerant** upload (mandatory per parent clarifications), **metadata listing** and **download** of uploads owned by the same account, lifecycle messaging when items expire under retention rules, predictable outcomes for unattended automation runs, plus **verification** artifacts that exercise the principal round-trip journeys.
- **Out of operational scope (unless reprioritized)**: Turning on **alternative third‑party identity** flows in production is **still optional**. For this milestone, that area is addressed by **explicit documentation** of what is unavailable, how administrators should reason about rollout, and that core upload/list/download journeys remain intact when those options are absent.
- **Consistency**: Parent functional intent and clarified limits (ownership of objects, denial without leaking peers’ existence, retention default and configurability from parent decisions) remain in force; this document states **additive** behavioral requirements for the deferred slice rather than contradicting **`001`**.
- **[NEEDS CLARIFICATION] markers**: none retained — defaults follow parent clarifications and industry norms documented in **`001`**.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Scripted upload after service interruption *(Priority: P2)*

A user or automation tool sends a large file via a console-oriented path using the same credential model as interactive use. Mid-transfer connectivity drops or the sending process stops. When the sender retries via the prescribed recovery mechanism, transmission continues from where it was validated without requiring the sender to transmit from byte zero everything that was already accepted.

**Why this priority**: scripted and recovery-sensitive scenarios are disproportionately affected by long transfers and unstable networks; honoring partial progress materially reduces downtime and egress cost.

**Independent Test**: use only scripted tooling against a deployed environment: authenticate, start uploading a large fixture, forcibly halt mid-transfer, then complete using the interruption-recovery workflow; observe success without re-sending accepted portions beyond what the verification contract allows.

**Acceptance Scenarios**:

1. **Given** valid credentials for an account authorized to ingest and a file within the negotiated maximum accepted size policy, **When** the scripted sender submits the file through the resumed multi-part workflow, **Then** ingestion completes successfully and yields a usable handle for downstream retrieval workflows.
2. **Given** the same file transfer was interrupted mid-way and the service had accepted ordered segments up to a known checkpoint, **When** the sender reconnects following the advertised recovery constraints, **Then** duplicate transmission of successfully accepted contiguous bytes is avoided for the resumed portion (subject to observable integrity rules).
3. **Given** malformed resume attempts or out‑of‑order arrivals outside the negotiated rules, **When** recovery is initiated, **Then** senders observe a deterministic, safe failure state from which retry or abandonment is straightforward.

---

### User Story 2 - Discover and retrieve one’s previously stored files *(Priority: P2)*

After ingestion, users can enumerate their retained items clearly enough to pick one, inspect basic metadata adequate for selection (name identity, sizing, timelines as agreed in product guidance), open or save the payload locally through the interactive web experience, or fetch it using the scripted tool with repeatable exit semantics.

**Why this priority**: the parent product clarified that “upload‑only fire and forget” is insufficient: owners must be able to **get their data back** through both interactive and scripted paths.

**Independent Test**: authenticate, ingest a known payload, then—without another ingest in the same run—list available items and retrieve the same item; confirm payload integrity (method at plan time, e.g., digest or size check) for both interactive and scripted paths.

**Acceptance Scenarios**:

1. **Given** an authenticated owner and a previously ingested item still within retention, **When** they request the item list, **Then** they see their item with selection-useful metadata and no other users’ items.
2. **Given** the same owner and item, **When** they trigger download from the web experience, **Then** the browser completes or surfaces a clear recoverable error without silent corruption.
3. **Given** the same owner and item, **When** they run the scripted download command, **Then** the process exits with a documented success or error code and leaves a local file only on success.
4. **Given** an unauthenticated session or a different account, **When** download is attempted for another owner’s handle, **Then** access is denied without revealing names, sizes, or existence of others’ items beyond a generic denial.
5. **Given** retention has removed an item, **When** the former owner requests it, **Then** they receive a clear denial that does not leak content hints.

---

### User Story 3 - Alternative third‑party identity as an optional modality *(Priority: P3)*

Where deployment policy intends sign‑in via a major hosted identity broker, administrators and operators receive written guidance stating whether operational sign‑through is activated, prerequisites, rollout caveats, and how password-based journeys remain unaffected. End users see no broken affordances—disabled options are visibly absent or clearly labeled unavailable per policy.

**Why this priority**: convenience for subsets of users, but MUST NOT block stabilization of ingestion and retrieval for password accounts.

**Independent Test**: review operator-facing narrative for completeness; in disabled mode confirm marketing/login surfaces imply no dangling provider buttons; enabled mode waits future scope—only documentation or explicit stubs without breaking core journeys.

**Acceptance Scenarios**:

1. **Given** deployments without broker sign‑in enabled, **When** administrators read onboarding material, **Then** broker-based sign‑in limitations and password-path guarantees are spelled out plainly.
2. **Given** roadmap intent to adopt broker flows later, **When** testers review documentation, **Then** prerequisites and rollout risks are enumerated without implying live availability prematurely.

---

### Edge Cases

- Files breaching negotiated maximum ingest size MUST be declined with actionable messaging even when clients attempt resume/chunk segmentation.
- Server storage exhaustion SHOULD surface unmistakable exhaustion errors without indefinite hangs.
- Parallel ingestions MUST NOT scramble ownership or manifests for the requesting account under typical contention.
- Access denials MUST follow the non‑enumeration principle for unrelated owners’ artifacts.
- Post‑TTL deletion MUST reconcile metadata and payloads so orphaned references do not falsely succeed retrieval.
- Batch/automation usage MUST define repeatable exit classifications for scripted CI consumers (success versus recoverable credential failure versus invariant violation).

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-F01**: The product MUST offer a scripted ingestion path interoperable with the service’s interruption‑tolerant ingestion contract within the negotiated per‑object ceiling (parent clarification: inclusive maximum typical of large single artifacts such as archival bundles).
- **FR-F02**: The recovery contract MUST insist on ordered, contiguous augmentation of payloads so integrity can be validated at completion boundaries.
- **FR-F03**: Upon successful scripted finalization of an ingestion session, the service MUST expose the same retrieval affordances already available through the browser-oriented path regarding ownership semantics.
- **FR-F04**: The product MUST furnish an authenticated enumeration of ingest records applicable solely to the active account with selection-grade metadata comparable to parental expectations on naming, sizing, time bounds aligned to lifecycle policy messaging.
- **FR-F05**: The product MUST support explicit owner-only download of payloads with streaming suitable for sizable objects while guarding against leakage through identifier guessing semantics.
- **FR-F06**: Denied attempts due to TTL expiry MUST articulate unavailability succinctly yet MUST NOT resurrect bytes or surrogate previews.
- **FR-F07**: Where third‑party delegated identity was classified optional in **`001`**, this milestone MUST document availability posture, prerequisites, UX expectations, operational toggles, and explicit statement of non-delivery unless separately scheduled—without regressing scenarios for password accounts.
- **FR-F08**: Delivery MUST include repeatable automated verification narratives covering login/password → ingest (browser or scripted conduit as appropriate) → list → retrieval, plus TTL-denied retrieval after simulated clock or shortened retention setups used only in harness contexts.
- **FR-F09**: Public machine-readable descriptors of capabilities MUST be reconciled with implemented behavior once this milestone merges (adjust either wording or implementations with traceable rationale communicated to integrators).

### Key Entities

- **Ingest Session**: ephemeral reservation tracking accepted contiguous bytes pending final artifact promotion.
- **Stored Artifact Metadata**: immutable handle and descriptive attributes surfaced for selection and authorization checks tied to initiating account.
- **Lifecycle Policy Exposure**: summarized retention horizons shown where low-friction contextual help is warranted (without overwhelming primary flows).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-F01**: End-to-end “ingest manageable fixture → list → retrieve comparable payload” scripted checks succeed on ≥95 % of reference repeated runs absent infrastructure faults.
- **SC-F02**: After a controlled scripted interruption midway through negotiating a maximal-size-class transfer, ≥90 % resume attempts complete acceptance without redoing contiguous bytes already affirmed by instrumentation logs or equivalent audit signals.
- **SC-F03**: ≥95 % of usability participants (subset ≥ 5 focusing on scripted operators) reconcile listed metadata with intended artifacts without escalating support when selecting downloads.
- **SC-F04**: Post-expiry scripted retrieval probes achieve 100 % deterministic denials devoid of unintended metadata leaks on the reference harness.
- **SC-F05**: Integration verification suites remain green continuously on mainline after stabilization (no regressions on browser-centric baseline delivered in **`001`**).
- **SC-F06**: External integrators auditing the formal capability description report zero unexplained deltas against observed behavior for enumerated routes—or receive committed documentation justifying purposeful staging.

---

## Assumptions

- Password credential ingestion remains authoritative for rollout until broker identity is prioritized as a discrete initiative.
- Retention horizon defaults harmonize with parent deployment guidance unless operators explicitly lengthen or shorten TTL with commensurate messaging updates.
- Platform-specific packaging (language toolchains, transports) rests with implementation planners and does not redefine user obligations captured here beyond measurable outcomes above.
- Parent clarifications restricting cross-user visibility survive unchanged; numbering of earlier functional labels in **`001`** remains canonical for regressions referencing original traceability matrices.
