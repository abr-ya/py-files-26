---

description: "Task list for Network File Upload Client MVP implementation"
---

# Tasks: Network File Upload Client

**Input**: Design documents from `/specs/001-network-file-upload-client/`  
**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [data-model.md](./data-model.md), [contracts/openapi.yaml](./contracts/openapi.yaml), [research.md](./research.md), alignment with `.specify/memory/constitution.md`

**Tests**: Minimal pytest coverage is included for constitution Principle IV (verification discipline); extend as needed.

**Organization**: Phases follow user-story priorities from `spec.md` (US1 P1 → US2/US3 P2 → US4 P3 MAY deferred).

**Delivery boundary (this PR / branch closure)**: Implements **Phase 1–3** only — tasks **`T001`–`T020`** (Setup, Foundational, browser MVP). Deferred work **`T021`–`T035`** lives in **[`specs/002-network-file-upload-follow-on/tasks.md`](../002-network-file-upload-follow-on/tasks.md)** for the next milestone.

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

- [x] T005 Implement environment-backed settings (`STORAGE_ROOT`, `JWT_SECRET`, `ALLOW_SELF_REGISTRATION`, `RETENTION_DAYS`, `MAX_UPLOAD_BYTES`) in `server/src/py_files_server/settings.py`
- [x] T006 Implement SQLAlchemy `engine`, session factory, and FastAPI dependency `get_db` in `server/src/py_files_server/db.py`
- [x] T007 Implement ORM models `User`, `StoredUploadObject`, `UploadSession` matching specs/001-network-file-upload-client/data-model.md in `server/src/py_files_server/models/` (split files OK under package `models/`)
- [x] T008 Implement startup schema creation or Alembic baseline migration so SQLite tables exist before routes run (`server/src/py_files_server/models/__init__.py` import side-effect or dedicated `server/src/py_files_server/migrate.py`)
- [x] T009 Implement password hashing/verification helpers (bcrypt) in `server/src/py_files_server/services/password.py`
- [x] T010 Implement JWT create/decode helpers and OAuth2-password style login expectations in `server/src/py_files_server/services/jwt.py`
- [x] T011 Implement filesystem helpers safe-join under `STORAGE_ROOT`, blob dirs, temp partial paths for upload sessions in `server/src/py_files_server/services/fs_storage.py`
- [x] T012 Implement TTL purge routine deleting expired `StoredUploadObject` rows and filesystem blobs (blob-first or row-first ordering per data-model validation notes) in `server/src/py_files_server/services/purge.py`
- [x] T013 Wire FastAPI app factory: include lifespan asyncio periodic TTL sweep, structured logging without logging file contents, mount `/api/v1` routers in `server/src/py_files_server/main.py`
- [x] T014 Implement FastAPI dependency `get_current_user` extracting Bearer JWT in `server/src/py_files_server/api/deps.py`
- [x] T015 Implement `/api/v1/auth/register` and `/api/v1/auth/login` per specs/001-network-file-upload-client/contracts/openapi.yaml with FR-010 gating self-registration in `server/src/py_files_server/api/routes/auth.py`

**Checkpoint**: Database models exist; auth endpoints usable with JWT; TTL sweep hooked (may be no-op until objects exist).

---

## Phase 3: User Story 1 — Authenticated upload from the browser (Priority: P1) 🎯 MVP

**Goal**: Password login (and optional registration when enabled) plus browser-based multipart upload with visible progress and outcome per FR-002 FR-004.

**Independent Test**: Using only the web UI: register/login (if allowed), upload ≤100 MB fixture file, see success or clear error without CLI.

### Implementation for User Story 1

- [x] T016 [US1] Implement `POST /api/v1/objects` multipart upload handling streaming to disk and persisting `StoredUploadObject` with `expires_at` from retention settings in `server/src/py_files_server/api/routes/objects.py`
- [x] T017 [US1] Enforce `MAX_UPLOAD_BYTES` and return FR-009-compatible errors before/during ingest in `server/src/py_files_server/api/routes/objects.py`
- [x] T018 [US1] Add minimal login/register/upload HTML shell per FR-004 progress needs in `frontend/templates/index.html`
- [x] T019 [US1] Implement vanilla JS auth + multipart upload + progress/fetch error display (no React/Vue) in `frontend/static/app.js`
- [x] T020 [US1] Serve static/templates from FastAPI (`StaticFiles`, `Jinja2Templates`) wired in `server/src/py_files_server/main.py`

**Checkpoint**: Story 1 acceptance scenarios in specs/001-network-file-upload-client/spec.md are demonstrable via browser only.

---

## Follow-on (deferred — next feature milestone)

Phases **4–7** and tasks **`T021`–`T035`** (CLI resume, download/list, OAuth MAY docs, polish) are **not** in scope for this increment.

→ **[`specs/002-network-file-upload-follow-on/spec.md`](../002-network-file-upload-follow-on/spec.md)** · **[`specs/002-network-file-upload-follow-on/tasks.md`](../002-network-file-upload-follow-on/tasks.md)**

---

## Dependencies (Story Completion Order)

```text
Phase 1 (Setup)
    → Phase 2 (Foundational)
        → Phase 3 [US1] Browser MVP   ✅ this increment / PR
        → specs/002 …                 Phase 4–7 (T021–T035)
```

Further sequencing for **`T021`–`T035`**: see **`specs/002-network-file-upload-follow-on/tasks.md`**.

---

## Parallel Execution Examples

- After **T007**: model files under `models/` may be edited in parallel **if** developers coordinate FK import order—otherwise keep single assignee.
- **T018** and **T019** (HTML + JS) can proceed in parallel once **T016** response contract is stable.

---

## Implementation Strategy

1. Land **Phase 1–2** so auth + DB + TTL loop are real.
2. Ship **US1** as vertical slice (demonstrable demo) — **this branch / PR**.
3. Continue with **`specs/002-network-file-upload-follow-on/`** for US2–US4 and polish (**`T021`–`T035`**).

---

## Suggested MVP Scope

Increment merged under **`001-network-file-upload-client`**: complete through **Phase 3 (US1)** plus minimal health check from Phase 2 — P1 browser upload path. Full **Variant C** (download round-trip, CLI resume from original product framing) is tracked under **`002-network-file-upload-follow-on`**.
