# Quickstart: py-files MVP (implemented layout)

Minimal steps for a **developer** running the backend, browser UI, and Python CLI locally. Match `plan.md` **Project Structure** (FastAPI under `server/`, static UI under `frontend/`, CLI under `clients/python/`).

## Prerequisites

- Python **3.11+**
- TLS for anything beyond **loopback** in production (`http://127.0.0.1` OK for smoke tests only).

## 1. Environment variables

Resolved by pydantic-settings (see `server/src/py_files_server/settings.py`). Common overrides:

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | SQLAlchemy URL (default SQLite file under `./var/` if unset relative to cwd) |
| `STORAGE_ROOT` | Root for `blobs/` and `partials/` |
| `JWT_SECRET` | **Required** sensible value outside dev |
| `ALLOW_SELF_REGISTRATION` | `true` / `false` (FR-010) |
| `RETENTION_DAYS` | Default **30** (TTL envelope for stored objects) |
| `MAX_UPLOAD_BYTES` | Per-object ceiling (default **1_000_000_000**) |

## 2. Install and run the API + web UI shell

From the repository root:

```bash
cd server
uv venv && . .venv/bin/activate           # optional; plain python -m venv .venv works too
uv pip install -e ".[dev]"                  # or: pip install -e ".[dev]"
uv run uvicorn py_files_server.main:app --reload --host 127.0.0.1 --port 8000
```

Open **`http://127.0.0.1:8000/`** — `GET /` serves **`frontend/templates/index.html`** with static assets mounted at **`/static`** from **`frontend/static/`** (`app.js`, `style.css`).

Health check lives **outside** the versioned JSON API root: **`GET http://127.0.0.1:8000/health`** (not described in **`contracts/openapi.yaml`**, which documents **`/api/v1` only**).

## 3. HTTP smoke (JWT)

Adjust host/port if needed.

```bash
BASE=http://127.0.0.1:8000

curl -sS -X POST "$BASE/api/v1/auth/register" \
  -H 'Content-Type: application/json' \
  -d '{"login":"demo","password":"change-me-strong"}'

curl -sS -X POST "$BASE/api/v1/auth/login" \
  -H 'Content-Type: application/json' \
  -d '{"login":"demo","password":"change-me-strong"}'
```

Take `access_token` from the login JSON and attach **`Authorization: Bearer <token>`** for:

- **`GET /api/v1/objects`** (list metadata)
- **`POST /api/v1/objects`** (multipart field **`file`**)
- **`GET /api/v1/objects/{id}`** · **`GET /api/v1/objects/{id}/content`**
- Resumable path: **`/api/v1/upload-sessions`** (see **`contracts/openapi.yaml`**).

## 4. CLI (`pyfiles`)

Uses **JWT** persisted to **`~/.config/py-files/config.json`** on Unix and **`%APPDATA%\py-files\config.json`** on Windows unless **`--config`** is passed.

```bash
cd clients/python
uv pip install -e .                           # or: pip install -e .

pyfiles login --base-url http://127.0.0.1:8000 --login demo --password 'change-me-strong'
pyfiles upload ./sample.bin                   # resumable path; writes sidecar sample.bin.pyfiles-session
pyfiles download <object-uuid-from-upload> -o ./out.bin
```

## 5. Automated tests

```bash
cd server
uv run pytest -q                  # discovers tests/, including integration/
```

(Optional) Contract-heavy validation (Schemathesis, etc.) is left for broader CI hardening (`plan.md`).
