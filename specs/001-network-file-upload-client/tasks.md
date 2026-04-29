---

description: "Task list for Network File Upload Client MVP implementation"
---

# Tasks: Network File Upload Client

**Input**: Design documents from `/specs/001-network-file-upload-client/`  
**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [data-model.md](./data-model.md), [contracts/openapi.yaml](./contracts/openapi.yaml), [research.md](./research.md), alignment with `.specify/memory/constitution.md`

**Tests**: Minimal pytest coverage is included for constitution Principle IV (verification discipline); extend as needed.

**Organization**: Phases follow user-story priorities from `spec.md` (US1 P1 → US2/US3 P2 → US4 P3 MAY deferred).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no blocking deps inside phase)
- **[Story]**: User story label `[US1]`… only on story phases (not Setup / Foundational / Polish)

## Path Conventions

Paths follow [plan.md](./plan.md): `server/src/py_files_server/`, `frontend/static/`, `frontend/templates/`, `clients/python/src/py_files_cli/`, `server/tests/`.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Repository skeleton matching the implementation plan.

- [x] T001 Create directory layout `server/src/py_files_server/{api/routes,models,services}`, `server/tests/`, `frontend/static/`, `frontend/templates/`, `clients/python/src/py_files_cli/commands/` per specs/001-network-file-upload-client/plan.md
- [x] T002 Add `server/pyproject.toml` (or `server/requirements.txt`) with FastAPI, Uvicorn, SQLAlchemy, pydantic-settings, passlib[bcrypt], python-jose[cryptography], python-multipart, httpx, pytest, pytest-asyncio as listed in specs/001-network-file-upload-client/plan.md
- [x] T003 Add `clients/python/pyproject.toml` declaring package `py-files-cli` (or `py_files_cli`) with runtime dependency `requests` and console script entrypoint per specs/001-network-file-upload-client/plan.md
- [x] T004 Add `server/tests/conftest.py` with pytest-asyncio configuration and optional httpx `AsyncClient` fixture factory targeted at `http://127.0.0.1:8000` for API tests

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared backend infrastructure required before user-story endpoints behave consistently.

**⚠️ CRITICAL**: Complete this phase before declaring any user story done.

- [ ] T005 Implement environment-backed settings (`STORAGE_ROOT`, `JWT_SECRET`, `ALLOW_SELF_REGISTRATION`, `RETENTION_DAYS`, `MAX_UPLOAD_BYTES`) in `server/src/py_files_server/settings.py`
- [ ] T006 Implement SQLAlchemy `engine`, session factory, and FastAPI dependency `get_db` in `server/src/py_files_server/db.py`
- [ ] T007 Implement ORM models `User`, `StoredUploadObject`, `UploadSession` matching specs/001-network-file-upload-client/data-model.md in `server/src/py_files_server/models/` (split files OK under package `models/`)
- [ ] T008 Implement startup schema creation or Alembic baseline migration so SQLite tables exist before routes run (`server/src/py_files_server/models/__init__.py` import side-effect or dedicated `server/src/py_files_server/migrate.py`)
- [ ] T009 Implement password hashing/verification helpers (bcrypt) in `server/src/py_files_server/services/password.py`
- [ ] T010 Implement JWT create/decode helpers and OAuth2-password style login expectations in `server/src/py_files_server/services/jwt.py`
- [ ] T011 Implement filesystem helpers safe-join under `STORAGE_ROOT`, blob dirs, temp partial paths for upload sessions in `server/src/py_files_server/services/fs_storage.py`
- [ ] T012 Implement TTL purge routine deleting expired `StoredUploadObject` rows and filesystem blobs (blob-first or row-first ordering per data-model validation notes) in `server/src/py_files_server/services/purge.py`
- [ ] T013 Wire FastAPI app factory: include lifespan asyncio periodic TTL sweep, structured logging without logging file contents, mount `/api/v1` routers in `server/src/py_files_server/main.py`
- [ ] T014 Implement FastAPI dependency `get_current_user` extracting Bearer JWT in `server/src/py_files_server/api/deps.py`
- [ ] T015 Implement `/api/v1/auth/register` and `/api/v1/auth/login` per specs/001-network-file-upload-client/contracts/openapi.yaml with FR-010 gating self-registration in `server/src/py_files_server/api/routes/auth.py`

**Checkpoint**: Database models exist; auth endpoints usable with JWT; TTL sweep hooked (may be no-op until objects exist).

---

## Phase 3: User Story 1 — Authenticated upload from the browser (Priority: P1) 🎯 MVP

**Goal**: Password login (and optional registration when enabled) plus browser-based multipart upload with visible progress and outcome per FR-002 FR-004.

**Independent Test**: Using only the web UI: register/login (if allowed), upload ≤100 MB fixture file, see success or clear error without CLI.

### Implementation for User Story 1

- [ ] T016 [US1] Implement `POST /api/v1/objects` multipart upload handling streaming to disk and persisting `StoredUploadObject` with `expires_at` from retention settings in `server/src/py_files_server/api/routes/objects.py`
- [ ] T017 [US1] Enforce `MAX_UPLOAD_BYTES` and return FR-009-compatible errors before/during ingest in `server/src/py_files_server/api/routes/objects.py`
- [ ] T018 [US1] Add minimal login/register/upload HTML shell per FR-004 progress needs in `frontend/templates/index.html`
- [ ] T019 [US1] Implement vanilla JS auth + multipart upload + progress/fetch error display (no React/Vue) in `frontend/static/app.js`
- [ ] T020 [US1] Serve static/templates from FastAPI (`StaticFiles`, `Jinja2Templates`) wired in `server/src/py_files_server/main.py`

**Checkpoint**: Story 1 acceptance scenarios in specs/001-network-file-upload-client/spec.md are demonstrable via browser only.

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
Phase 1 (Setup)
    → Phase 2 (Foundational)
        → Phase 3 [US1] Browser MVP  ─┐
        → Phase 4 [US2] CLI resume    ├→ Phase 5 [US3] Download lists round-trip (needs StoredUploadObject from US1/US2)
        → Phase 6 [US4] Docs-only MAY
    → Phase 7 Polish (OpenAPI parity + integration tests)
```

US2 can start after Foundational regardless of US3 but logically follows MVP browser upload; US3 requires objects existing—complete US1 minimum before US3 acceptance.

---

## Parallel Execution Examples

- After **T007**: model files under `models/` may be edited in parallel **if** developers coordinate FK import order—otherwise keep single assignee.
- **T018** and **T019** (HTML + JS) can proceed in parallel once **T016** response contract is stable.
- **T025** and **T026** can proceed in parallel after **T021–T023** backend session API is stable.

---

## Implementation Strategy

1. Land **Phase 1–2** so auth + DB + TTL loop are real.  
2. Ship **US1** as vertical slice (demonstrable demo).  
3. Add **US2** resumable sessions + CLI upload.  
4. Expose **US3** download/list + CLI download.  
5. Document **US4** deferral; close with polish + integration tests + OpenAPI drift fix.

---

## Suggested MVP Scope

First shippable increment: complete through **Phase 3 (US1)** plus minimal health check from Phase 2—delivers P1 browser upload path per spec.
