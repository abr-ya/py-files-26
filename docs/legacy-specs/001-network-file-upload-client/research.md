# Research: Network File Upload Client

Decisions resolve technical unknowns from `plan.md` Technical Context (Phase 0).

---

### Decision: Backend framework — FastAPI + Uvicorn

**Rationale**: Matches constitution Principle 7 (REST-shaped JSON APIs with explicit versioning). FastAPI generates OpenAPI automatically and aligns with Python-first repo assumptions.

**Alternatives considered**: Flask (manual OpenAPI upkeep); Django (heavier ORM/cms defaults); Starlette alone (more boilerplate).

---

### Decision: Metadata database — SQLite (SQLModel/SQLAlchemy) for MVP

**Rationale**: Single-binary deployments; sufficient for MVP concurrency when paired with WAL mode and bounded workers. Tables hold users, sessions, stored-object metadata, and resumable upload sessions.

**Alternatives considered**: PostgreSQL (preferred when scaling horizontally or HA required—migrate path documented in plan).

---

### Decision: Blob storage — local filesystem under configurable `STORAGE_ROOT`

**Rationale**: Simple operations for TTL sweeping and checksum verification; aligns with Principle V until object-store requirements appear.

**Alternatives considered**: S3-compatible API (add when multi-node or durability SLA demands).

---

### Decision: Authentication — bcrypt password hashes + JWT access tokens (Bearer)

**Rationale**: Satisfies Principle 5 (no plaintext passwords over the wire—TLS enforced for HTTP APIs); avoids sending raw passwords beyond `/auth/login` body over HTTPS only.

**Alternatives considered**: Session cookies only (fine for browser but awkward for CLI—JWT shared across surfaces).

---

### Decision: Configurable registration — `ALLOW_SELF_REGISTRATION` env flag

**Rationale**: Implements FR-010 hybrid provisioning without duplicate products.

---

### Decision: Resumable uploads — upload-session resource + ranged chunk append

**Rationale**: CLI MUST resume per FR-011 without adopting full tus middleware stack in MVP. Pattern:

1. `POST /api/v1/upload-sessions` with declared `filename`, `total_size`.
2. `PATCH /api/v1/upload-sessions/{id}` with `Content-Type: application/octet-stream`, `Upload-Offset` (or `Content-Range`) header appending bytes server verifies contiguous assembly up to `total_size`.
3. `POST /api/v1/upload-sessions/{id}/complete` verifies size/checksum and promotes to stored object.

Browser MAY use simple multipart `POST /api/v1/objects` single-shot upload without sessions.

**Alternatives considered**: tusd sidecar (extra deployment moving parts); generic multipart-only (fails CLI resume MUST).

---

### Decision: TTL enforcement — asyncio periodic sweep + deletion job on configurable interval

**Rationale**: FR-012 requires purge after retention window (default 30 days). Cron-friendly architecture allows systemd timer wrapping same CLI later.

---

### Decision: Browser UI — minimal vanilla JS + server-rendered HTML or static SPA-less pages served by FastAPI

**Rationale**: Constitution Principle 8 discourages React/Vue unless justified—complexity tracking stays empty.

---

### Decision: Python CLI package — `requests`, stdlib (`argparse`, `pathlib`); tqdm optional for progress

**Rationale**: Constitution Principle 8 baseline dependencies.

---

### Decision: Google OAuth — stubbed/documented only in MVP

**Rationale**: FR-006 MAY—omit implementation until login/password paths ship (tracked as future iteration in plan Summary).

---

### Decision: Observability — structured logging server-side; CLI logs operations without file contents

**Rationale**: Principles 9–10 (testability + transparent status).
