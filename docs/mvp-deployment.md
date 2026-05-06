# MVP: Running and Minimal VPS Deploy

Short guide for local runs and test deployments of **py-files** (FastAPI + SQLite + filesystem blobs). More detail on the dev setup: [`specs/001-network-file-upload-client/quickstart.md`](../specs/001-network-file-upload-client/quickstart.md).

## Server stack

- Python **3.11+**
- **FastAPI**, **Uvicorn**, SQLAlchemy, Pydantic Settings, JWT
- Metadata: **SQLite** (`DATABASE_URL`)
- Files: **`STORAGE_ROOT`** directory (blob storage and resumable upload chunks)
- Web shell: `frontend/templates` and `frontend/static` are loaded from the **repository root** (`server/` and `frontend/` must stay side by side as in the cloned repo)

Dependencies and installation: `server/pyproject.toml`, `server/README.md`.

## Environment variables

Resolved via **pydantic-settings** (`server/src/py_files_server/settings.py`); supports a **`.env`** file (UTF-8). `.env` is resolved relative to the **process working directory**. For deterministic behavior either set systemd `WorkingDirectory` to `server/` or use **absolute** paths in variables.

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | SQLAlchemy URL; defaults to SQLite at `./var/py_files.db` relative to cwd |
| `STORAGE_ROOT` | Root for on-disk `blobs/` and `partials/` |
| `JWT_SECRET` | JWT signing secret; **change** the default anywhere outside casual dev |
| `ALLOW_SELF_REGISTRATION` | `true` / `false` — whether users may self-register |
| `RETENTION_DAYS` | Object retention TTL (default **30**) |
| `MAX_UPLOAD_BYTES` | Maximum size per stored object (default **1_000_000_000**) |
| `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `TTL_PURGE_INTERVAL_SECONDS` | Usually left default |

Spec and quickstart: for traffic not bound to loopback, **HTTPS** behind a TLS terminator (Nginx, Caddy, etc.) is expected.

### Example `.env`

Save as `server/.env` and run Uvicorn with working directory `server/` (or pass the same variables via systemd / the shell). Lines starting with `#` are comments; values must stay on one line.

```bash
# --- Required beyond casual dev ---
# Long random secret (example: openssl rand -hex 32)
JWT_SECRET=replace-with-a-long-random-string

# --- Strongly recommended in production / VPS ---
# SQLite: use four slashes after sqlite: for an absolute path on Linux/macOS (sqlite:////absolute/path)
DATABASE_URL=sqlite:////opt/py-files/var/py_files.db
STORAGE_ROOT=/opt/py-files/var/storage

# --- Access policy ---
ALLOW_SELF_REGISTRATION=true

# --- Optional tweaks (omit to use defaults) ---
RETENTION_DAYS=30
MAX_UPLOAD_BYTES=1000000000
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
TTL_PURGE_INTERVAL_SECONDS=3600
```

For a **quick local smoke test** without a custom layout you can omit the file entirely (defaults apply), or copy the above with relative paths aligned to cwd:

```bash
JWT_SECRET=dev-only-change-me
DATABASE_URL=sqlite:///./var/py_files.db
STORAGE_ROOT=./var/storage
ALLOW_SELF_REGISTRATION=true
```

---

## Local run (development / smoke)

From the **repository root**:

```bash
cd server
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"     # production server only: pip install -e .
uvicorn py_files_server.main:app --reload --host 127.0.0.1 --port 8000
```

- UI: `http://127.0.0.1:8000/`
- Health (not in OpenAPI): `GET http://127.0.0.1:8000/health`

---

## Minimal VPS deploy (MVP smoke test)

Good for fast validation; when exposed to the public internet prefer adding a reverse proxy and TLS straight away (next section).

1. **OS** (Ubuntu example): install `python3` (3.11+), `python3-venv`, `git`.
2. **Clone the full repository** so `server/` and `frontend/` remain together.
3. **Install the app**:

   ```bash
   cd server
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -e .
   ```

4. **Configure** `server/.env` (or systemd `Environment`): at minimum use a strong `JWT_SECRET`; set `ALLOW_SELF_REGISTRATION=true` if you want open test registration; optional absolute `DATABASE_URL` and `STORAGE_ROOT`.
5. **Run** from `server/` with the venv active:

   ```bash
   uvicorn py_files_server.main:app --host 0.0.0.0 --port 8000
   ```

   Open the listener port on the firewall (temporary setup). Respect proxy limits and timeouts for large uploads.

**SQLite:** multiple Uvicorn workers can contend on locks; a simple MVP test usually uses **one** process.

---

## Recommended hardening step

- Bind Uvicorn to **127.0.0.1** and publish only **80/443** through **Nginx** or **Caddy** with HTTPS.
- Raise the proxy’s max request body size to **at least** `MAX_UPLOAD_BYTES` and lengthen timeouts where needed.
- Run under **systemd**: `WorkingDirectory=<path>/server`, `ExecStart=<path>/server/.venv/bin/uvicorn ...`, dedicated UNIX user with least privilege over data and DB files.

## Backups (once you keep data)

Back up together: the SQLite file from `DATABASE_URL` and everything under `STORAGE_ROOT`.

## CLI vs server

The **`pyfiles`** client (`clients/python`) takes `--base-url` pointing at your API (`http://localhost:8000`, or `https://…` after the proxy). Default config paths: quickstart (`~/.config/py-files/` on Unix).
