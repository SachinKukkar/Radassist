from fastapi import FastAPI
from fastapi.testclient import TestClient

from app import __version__
from app.api.deps import get_dependency_checks
from app.core.config import Settings


def passing_check(settings: Settings) -> None:
    """A fake dependency check that always succeeds."""


def failing_check(settings: Settings) -> None:
    """A fake dependency check that always fails."""
    raise ConnectionError("dependency unreachable")


def test_liveness_returns_ok_and_version(client: TestClient) -> None:
    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": __version__}


def test_readiness_returns_200_when_all_dependencies_are_healthy(
    app: FastAPI, client: TestClient
) -> None:
    app.dependency_overrides[get_dependency_checks] = lambda: {
        "database": passing_check,
        "redis": passing_check,
    }

    response = client.get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "checks": {"database": "ok", "redis": "ok"}}


def test_readiness_returns_503_when_a_dependency_fails(app: FastAPI, client: TestClient) -> None:
    app.dependency_overrides[get_dependency_checks] = lambda: {
        "database": passing_check,
        "redis": failing_check,
    }

    response = client.get("/health/ready")

    assert response.status_code == 503
    assert response.json() == {
        "status": "degraded",
        "checks": {"database": "ok", "redis": "error"},
    }


def test_openapi_schema_is_served_under_versioned_prefix(client: TestClient) -> None:
    response = client.get("/api/v1/openapi.json")

    assert response.status_code == 200
    assert response.json()["info"]["title"] == "RadAssist API"
