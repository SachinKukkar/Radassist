from fastapi import APIRouter

from app import __version__
from app.schemas.health import LivenessResponse, ReadinessResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live", summary="Liveness probe")
async def live() -> LivenessResponse:
    """Return 200 while the process is running. Docker restarts the container if this fails."""
    return LivenessResponse(version=__version__)


@router.get("/ready", summary="Readiness probe")
async def ready() -> ReadinessResponse:
    """Return 200 when the app can serve traffic.

    From Step 6 onward this will check the database, Redis and object storage.
    """
    return ReadinessResponse()
