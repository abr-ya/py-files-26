# Repository Guidelines

## Project Structure & Module Organization

This repository contains a small network file upload system split by surface:

- `server/`: FastAPI backend package (`src/py_files_server`) with API routes, SQLAlchemy models, services, settings, and pytest tests in `server/tests`.
- `frontend/`: server-rendered browser UI assets, with templates in `frontend/templates` and static JavaScript/CSS in `frontend/static`.
- `clients/python/`: installable Python CLI package (`src/py_files_cli`) exposing the `pyfiles` command.
- `specs/`: product/specification work, task breakdowns, quickstart notes, and OpenAPI contract.
- `docs/`: operational and PR/deployment documentation.

Keep changes near the surface they affect. Update specs or docs when behavior, APIs, or deployment steps change.

## OpenSpec & Token Discipline

Before OpenSpec, backlog, or planning work, follow `docs/agent-openspec-token-guide.md`. In short: start from live repo state, preserve existing feature numbering, read only the smallest useful files, keep chat updates concise, and store durable planning state in repository markdown rather than long chat messages.

## Build, Test, and Development Commands

Use Python 3.11 or newer.

```bash
cd server
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
uvicorn py_files_server.main:app --reload
```

`pytest` runs the server test suite configured in `server/pyproject.toml`. `uvicorn` starts the API and browser UI locally.

```bash
cd clients/python
python -m venv .venv && source .venv/bin/activate
pip install -e .
pyfiles --help
```

Use the CLI install when working on client commands or packaging.

## Coding Style & Naming Conventions

Follow idiomatic Python with 4-space indentation, type hints for public functions, and short module docstrings where useful. Package names use lowercase snake case (`py_files_server`, `py_files_cli`). Tests and functions should use descriptive snake case, for example `test_health_ok`.

Prefer explicit service modules under `server/src/py_files_server/services` for reusable behavior. Keep FastAPI route handlers thin and place request/response models under `api/schemas`.

## Testing Guidelines

Server tests use `pytest`, `pytest-asyncio`, `httpx`, and FastAPI `TestClient`. Add tests in `server/tests` with filenames matching `test_*.py`. For API changes, cover status codes, JSON bodies, auth behavior, and storage/database side effects where relevant.

Tests set temporary `DATABASE_URL`, `STORAGE_ROOT`, and `JWT_SECRET` in `conftest.py`; avoid hard-coding local paths or secrets.

## Commit & Pull Request Guidelines

Git history uses concise conventional-style messages such as `feat(server): ...`, `docs(spec): ...`, and `feat(us1): ...`. Keep commits focused and include the affected area in the scope when helpful.

Pull requests should summarize behavior changes, list validation commands run, and link related spec tasks or issues. Include screenshots when changing `frontend/` UI behavior and mention any new environment variables or migration/deployment steps.

## Security & Configuration Tips

Runtime settings come from environment variables or an optional `.env` file via `server/src/py_files_server/settings.py`. Always override the development `JWT_SECRET` outside local testing. Do not commit generated storage, SQLite databases, secrets, or virtual environments.
