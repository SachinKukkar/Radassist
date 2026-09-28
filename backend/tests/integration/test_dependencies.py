"""Integration tests: need the real services from compose.yaml (`make up` or `make deps`)."""

import pytest

from app.core.config import Settings
from app.services.health import check_database, check_object_storage, check_redis

pytestmark = pytest.mark.integration


@pytest.fixture
def local_settings() -> Settings:
    """Default settings point at the Compose services published on localhost."""
    return Settings(_env_file=None)


def test_database_is_reachable(local_settings: Settings) -> None:
    check_database(local_settings)  # raises if PostgreSQL is unreachable


def test_redis_is_reachable(local_settings: Settings) -> None:
    check_redis(local_settings)  # raises if Redis is unreachable


def test_object_storage_bucket_exists(local_settings: Settings) -> None:
    check_object_storage(local_settings)  # raises if S3 or the bucket is unavailable
