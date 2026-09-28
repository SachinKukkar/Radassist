import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import __version__
from app.api.routes import health
from app.core.config import Settings, get_settings
from app.core.logging import setup_logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Run code at startup (before yield) and shutdown (after yield)."""
    settings: Settings = app.state.settings
    logger.info("Starting %s v%s (env=%s)", settings.app_name, __version__, settings.environment)
    yield
    logger.info("Shutting down %s", settings.app_name)


def create_app(settings: Settings | None = None) -> FastAPI:
    """Application factory. Pass `settings` to override configuration, e.g. in tests."""
    if settings is None:
        settings = get_settings()
    setup_logging(level=settings.log_level, json_logs=settings.log_json)

    app = FastAPI(
        title=settings.app_name,
        version=__version__,
        debug=settings.debug,
        lifespan=lifespan,
        openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    )
    app.state.settings = settings
    app.include_router(health.router)
    return app


app = create_app()
