from __future__ import annotations

import sys
import logging
from pathlib import Path
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from app.core.config import settings  # noqa: E402
from app.db.session import engine  # noqa: E402
from app.models.base import BaseDB  # noqa: E402

logger = logging.getLogger(__name__)

API_V1_PREFIX = "/api/v1"
API_DESCRIPTION = "Backend for planning trips and visiting art places from the Art Institute of Chicago."

_OPENAPI_TAGS = [
    {"name": "Health", "description": "Service availability."},
    {"name": "Projects", "description": "Trip planning projects."},
]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("Database: creating tables if missing")
    async with engine.begin() as conn:
        await conn.run_sync(BaseDB.metadata.create_all)

    yield

    logger.info("Database: disposing engine")
    await engine.dispose()


def _include_routers(application: FastAPI) -> None:
    from app.api.routes.projects import router as project_router
    from app.api.routes.places import router as place_router

    application.include_router(
        project_router,
        prefix=f"{API_V1_PREFIX}/projects",
        tags=["Projects"],
    )
    application.include_router(
        place_router,
        prefix=f"{API_V1_PREFIX}/places",
        tags=["Places"],
    )


def _register_health_routes(application: FastAPI) -> None:
    @application.get("/health", tags=["Health"])
    async def health_check() -> dict[str, str]:
        """Return service health status."""
        return {"status": "ok", "message": "Service is up and running"}


def create_app() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        description=API_DESCRIPTION,
        version="1.0.0",
        openapi_version="3.1.0",
        lifespan=lifespan,
        openapi_tags=_OPENAPI_TAGS,
    )
    _include_routers(application)
    _register_health_routes(application)
    return application


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
