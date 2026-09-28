from fastapi import APIRouter, Response, status

from app import __version__
from app.api.deps import DependencyChecksDep, SettingsDep
from app.schemas.health import LivenessResponse, ReadinessResponse
from app.services.health import run_checks

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live", summary="Liveness probe")
async def live() -> LivenessResponse:
    """Return 200 while the process is running. Docker restarts the container if this fails."""
    return LivenessResponse(version=__version__)


@router.get(
    "/ready",
    summary="Readiness probe",
    responses={status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ReadinessResponse}},
)
def ready(
    response: Response, settings: SettingsDep, checks: DependencyChecksDep
) -> ReadinessResponse:
    """Return 200 if every dependency is reachable, otherwise 503.

    This is a plain `def` (not `async def`) because the checks use blocking network clients.
    FastAPI runs it in a worker thread, so the event loop stays free for other requests.
    """
    results = run_checks(settings, checks)
    if all(result == "ok" for result in results.values()):
        return ReadinessResponse(status="ok", checks=results)
    response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return ReadinessResponse(status="degraded", checks=results)
