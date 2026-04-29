"""FastAPI application entry."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, suppress
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.routing import APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from py_files_server.api.routes import auth as auth_routes
from py_files_server.api.routes import objects as objects_routes
from py_files_server.db import SessionLocal, init_db
from py_files_server.services.fs_storage import ensure_storage_layout
from py_files_server.services.purge import purge_expired_upload_objects
from py_files_server.settings import Settings, get_settings

logger = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).resolve().parents[3]
_FRONTEND_STATIC = _REPO_ROOT / "frontend" / "static"
_FRONTEND_TEMPLATES = _REPO_ROOT / "frontend" / "templates"


async def _purge_scheduler(settings: Settings) -> None:
    while True:
        await asyncio.sleep(float(settings.ttl_purge_interval_seconds))
        db = SessionLocal()
        try:
            deleted_count = purge_expired_upload_objects(db, settings)
            if deleted_count:
                logger.info("TTL purge removed %s expired object(s)", deleted_count)
        except Exception:
            logger.exception("TTL purge failed")
        finally:
            db.close()


def _ensure_sqlite_parent_dir(database_url: str) -> None:
    if not database_url.startswith("sqlite:///"):
        return
    tail = database_url.removeprefix("sqlite:///")
    db_file = Path(tail)
    if not db_file.is_absolute():
        db_file = Path.cwd() / db_file
    db_file.parent.mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:  # noqa: ARG001
    logging.basicConfig(level=logging.INFO)
    settings = get_settings()

    _ensure_sqlite_parent_dir(settings.database_url)

    settings.storage_root.mkdir(parents=True, exist_ok=True)
    ensure_storage_layout(settings.storage_root)

    init_db()

    purge_task = asyncio.create_task(_purge_scheduler(settings))
    logger.info("Application startup complete")
    yield
    purge_task.cancel()
    with suppress(asyncio.CancelledError):
        await purge_task
    logger.info("Application shutdown")


app = FastAPI(title="py-files-server", lifespan=lifespan)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_routes.router, prefix="/auth")
api_router.include_router(objects_routes.router, prefix="/objects")
app.include_router(api_router)

templates = Jinja2Templates(directory=str(_FRONTEND_TEMPLATES))
if _FRONTEND_STATIC.is_dir():
    app.mount("/static", StaticFiles(directory=str(_FRONTEND_STATIC)), name="static")


@app.get("/")
def index(request: Request):
    """Serve browser UI shell."""
    return templates.TemplateResponse(request, "index.html")


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness probe."""
    return {"status": "ok"}
