# Quickstart: Network File Upload Client (planned layout)

Targets developers validating MVP flows locally against the architecture in `plan.md`.

## Prerequisites

- Python **3.11+**
- TLS-capable reverse proxy recommended for production (local dev MAY use HTTP **only on loopback**—never ship credentials without TLS).

## 1. Layout (once implementation exists)

Expected repository surface (see `plan.md` **Project Structure**):

- `server/` — FastAPI application
- `frontend/static/` — vanilla JS + assets
- `clients/python/` — CLI package

## 2. Configure environment

| Variable | Purpose |
|----------|---------|
| `STORAGE_ROOT` | Directory for blob files + temp upload parts |
| `JWT_SECRET` | Symmetric signing key for access tokens |
| `ALLOW_SELF_REGISTRATION` | `true` / `false` (FR-010) |
| `RETENTION_DAYS` | Default `30` per spec |
| `MAX_UPLOAD_BYTES` | Default `1000000000` (1×10⁹ bytes) |

## 3. Run API (placeholder command)

```bash
cd server
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn py_files_server.main:app --reload --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/` for the static UI (once wired).

## 4. Smoke API

```bash
curl -s -X POST "$BASE/api/v1/auth/login" \
  -H 'Content-Type: application/json' \
  -d '{"login":"demo","password":"***"}'
```

Use returned `access_token` as `Authorization: Bearer …` for `/api/v1/objects` (see `contracts/openapi.yaml`).

## 5. CLI (placeholder)

```bash
pip install -e clients/python
pyfiles --base-url "$BASE" login
pyfiles upload ./sample.bin
pyfiles download <object-id> ./out.bin
```

## 6. Run tests

```bash
pytest -q
```

Contract tests SHOULD load `contracts/openapi.yaml` once `schemathesis` or `openapi-spec-validator` is added (per plan verification goals).
