# Implementation Plan: Network File Upload Client

**Branch**: `001-network-file-upload-client` | **Date**: 2026-04-29 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/001-network-file-upload-client/spec.md`

## Summary

Deliver an authenticated **network file upload and download** product with **browser** and **Python CLI** surfaces. MVP includes login/password auth, configurable registration policy, simple web UI, **single-shot uploads** for typical browser flows, **resumable chunked uploads** for CLI (mandatory per FR-011), stored-object listing/metadata sufficient to pick downloads, **30-day default TTL** with purge, and **OpenAPI-described** HTTP APIs under `/api/v1`. **Google OAuth** remains MAY—implementation deferred until core flows pass acceptance tests.

## Technical Context

**Language/Version**: Python **3.11+** (server + CLI); vanilla ES **browser baseline** (last-two-major browsers per constitution).

**Primary Dependencies**: **FastAPI**, **Uvicorn**, **SQLAlchemy/SQLModel** (SQLite MVP), **Pydantic v2**, **passlib[bcrypt]**, **python-jose** (JWT), **python-multipart**; CLI **`requests`**, stdlib `argparse`.

**Storage**: SQLite DB for metadata; local filesystem under **`STORAGE_ROOT`** for blobs and resumable partials.

**Testing**: **pytest**, **httpx** `AsyncClient` for API tests; CLI subprocess smoke tests; optional **Schemathesis** once endpoints stabilize.

**Target Platform**: Linux/macOS/Windows dev; production Linux container/VPS behind TLS terminator.

**Project Type**: multi-surface **`web-service` + CLI library**.

**Performance Goals**: sustained streaming throughput bounded by disk/network—not latency micro-optimization MVP; enumerate bulk-headroom targets post-load-test.

**Constraints**: single-object ≤ **1×10⁹ bytes** default; HTTPS/TLS mandatory outside localhost; JWT TTL reasonably short (e.g., 24 h access token MVP).

**Scale/Scope**: single-region MVP deployment; horizontal scaling deferred—SQLite acceptable until PostgreSQL migration triggered.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Per `.specify/memory/constitution.md`:

- **Workflow fidelity**: Artifacts remain under `specs/001-network-file-upload-client/` and align with `/speckit.*` sequencing—no waiver.
- **Authority**: Design respects Principles **5–11** (TLS passwords transport not plaintext logging file bodies; REST JSON metadata + octet-stream binaries; `/api/v1` versioning + maintained **OpenAPI** in `contracts/openapi.yaml`; Python CLI deps bounded to requests/stdlib baseline; vanilla JS UI **without React/Vue** unless tracked later under Complexity Tracking—none planned MVP).
- **Tests/increments**: Stories **P1–P4** remain independently verifiable—mapping preserved in tasks phase.
- **Verification**: Automated pytest suites planned per Principle IV— gaps limited to exploratory OAuth deferred explicitly below (future Complexity entry only when scoped).
- **Simplicity**: Architecture selects FastAPI monolith over microservices; filesystem storage vs object-store until scaling demands justify complexity.

*Post-design (Phase 1): gates remain satisfied—Google OAuth intentionally deferred as MAY scope.*

## Project Structure

### Documentation (this feature)

```text
specs/001-network-file-upload-client/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root — planned implementation layout)

```text
server/
├── pyproject.toml       # or requirements.txt bootstrap
├── src/
│   └── py_files_server/
│       ├── main.py              # FastAPI app factory + lifespan TTL sweep
│       ├── api/routes/          # auth, objects, upload_sessions
│       ├── models/              # SQLAlchemy models
│       ├── services/            # auth, storage, purge
│       └── settings.py          # pydantic-settings env binding
└── tests/
    ├── api/
    └── services/

frontend/
├── static/
│   ├── app.js
│   └── styles.css
└── templates/
    └── index.html               # minimal shell – fetch JSON APIs

clients/python/
├── pyproject.toml
├── src/py_files_cli/
│   ├── __main__.py
│   ├── commands/login.py
│   ├── commands/upload.py       # resumable session driver
│   └── commands/download.py
└── tests/

tests/
└── integration/                 # optional cross-package scenarios
```

**Structure Decision**: Split **`server/`**, **`frontend/` static assets**, and **`clients/python/`** packages so FastAPI backend + CLI evolve independently while sharing OpenAPI contracts—matches constitution separation (CLI deps minimal).

## Complexity Tracking

> No constitution violations requiring justification at this phase—OAuth MAY deliberately omitted.
