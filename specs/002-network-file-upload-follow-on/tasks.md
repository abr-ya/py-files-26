---

description: "Deferred tasks after Phase 3 browser MVP (moved from 001-network-file-upload-client)"
---

# Tasks: Network File Upload Client — Follow-on (`T021`–`T035`)

**Parent design**: [`specs/001-network-file-upload-client/`](../001-network-file-upload-client/) (plan, spec, data-model, contracts, research).

**Scope**: Everything below was **out of scope** for the PR that closes Phase **3** (`T001`–`T020`). Implement here on a dedicated branch / milestone.

---

## Phase 4: User Story 2 — Authenticated upload from CLI with resume (Priority: P2)

**Goal**: Resumable upload session flow (POST create, PATCH append with `Upload-Offset`, POST complete) per contracts and FR-011.

**Independent Test**: With API running, use CLI only: `pyfiles upload ./file.bin` interrupted mid-way, retry/resume completes without full resend.

### Implementation for User Story 2

- [ ] T021 [US2] Implement `POST /api/v1/upload-sessions`, `PATCH /api/v1/upload-sessions/{session_id}` (header `Upload-Offset`), `POST .../complete` per specs/001-network-file-upload-client/contracts/openapi.yaml in `server/src/py_files_server/api/routes/upload_sessions.py`
- [ ] T022 [US2] Implement contiguous chunk append + received byte accounting + session state machine in `server/src/py_files_server/services/upload_session_service.py`
- [ ] T023 [US2] Finalize session: promote to `StoredUploadObject`, compute optional sha256, delete temp partial in `server/src/py_files_server/services/upload_finalize.py`
- [ ] T024 [US2] Implement CLI entry `python -m py_files_cli` argparse root in `clients/python/src/py_files_cli/__main__.py`
- [ ] T025 [US2] Implement `clients/python/src/py_files_cli/commands/login.py` storing JWT from `/auth/login` in user config file under `~/.config/py-files/` (or cross-platform equivalent)
- [ ] T026 [US2] Implement resumable upload driver using `requests` sessions, `Upload-Offset` loop, tqdm-optional progress in `clients/python/src/py_files_cli/commands/upload.py`

**Checkpoint**: SC-006 measurable resumable CLI path available; no browser required to validate.

---

## Phase 5: User Story 3 — Download previously uploaded files (Priority: P2)

**Goal**: List owned objects metadata and download octet-stream bytes; deny others; TTL expiry message per FR-007 FR-008 FR-012.

**Independent Test**: Upload via any path, then list + download checksum match; attempt other user ID returns 404/403 without leaking metadata.

### Implementation for User Story 3

- [ ] T027 [US3] Implement `GET /api/v1/objects` listing `StoredUploadObject` for current user in `server/src/py_files_server/api/routes/objects.py`
- [ ] T028 [US3] Implement `GET /api/v1/objects/{object_id}` metadata and `GET /api/v1/objects/{object_id}/content` streaming download with ownership enforcement in `server/src/py_files_server/api/routes/objects.py`
- [ ] T029 [US3] Extend `frontend/static/app.js` to list objects and trigger browser download via authenticated fetch/FileSaver pattern
- [ ] T030 [US3] Implement `clients/python/src/py_files_cli/commands/download.py` writing file to disk with exit codes per spec SC-004

**Checkpoint**: Round-trip upload → download satisfies SC-005 when checksum implemented.

---

## Phase 6: User Story 4 — Optional Google sign-in (Priority: P3) MAY / Deferred

**Goal**: Track MAY scope explicitly—OAuth not in MVP implementation per specs/001-network-file-upload-client/plan.md.

- [ ] T031 [US4] Add short “OAuth deferred” subsection referencing FR-006 MAY to `specs/001-network-file-upload-client/plan.md` Summary or append **Deferred items** list (no runtime code until prioritized)

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Constitution Principle IV verification, OpenAPI parity, operator docs.

- [ ] T032 Sync implemented routes with schemas by reconciling drift vs specs/001-network-file-upload-client/contracts/openapi.yaml (adjust YAML or code—single source of truth documented in commit)
- [ ] T033 Add pytest integration covering login → multipart upload → list → download round-trip in `server/tests/integration/test_roundtrip.py`
- [ ] T034 Add pytest covering TTL denial path using mocked clock or shortened retention env in `server/tests/integration/test_ttl_denial.py`
- [ ] T035 Refresh runnable commands in specs/001-network-file-upload-client/quickstart.md against actual module/app paths after implementation

---

## Dependencies (Story Completion Order)

```text
Phase 4 [US2] CLI resume
    → Phase 5 [US3] Download lists round-trip (needs StoredUploadObject from US1/US2 paths)
Phase 6 [US4] Docs-only MAY
    → Phase 7 Polish (OpenAPI parity + integration tests)
```
