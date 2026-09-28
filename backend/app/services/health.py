import logging
from collections.abc import Callable, Mapping

import boto3
import psycopg
import redis
from botocore.config import Config

from app.core.config import Settings

logger = logging.getLogger(__name__)

# A check raises an exception if its dependency is unreachable; otherwise it returns None.
DependencyCheck = Callable[[Settings], None]


def check_database(settings: Settings) -> None:
    """Connect to PostgreSQL and run a trivial query."""
    with psycopg.connect(
        settings.database_url.get_secret_value(),
        connect_timeout=max(1, round(settings.health_check_timeout_seconds)),
    ) as connection:
        connection.execute("SELECT 1")


def check_redis(settings: Settings) -> None:
    """Connect to Redis and send PING."""
    client = redis.Redis.from_url(
        settings.redis_url,
        socket_connect_timeout=settings.health_check_timeout_seconds,
        socket_timeout=settings.health_check_timeout_seconds,
    )
    try:
        client.ping()
    finally:
        client.close()


def check_object_storage(settings: Settings) -> None:
    """Confirm the configured bucket exists and the credentials can access it."""
    client = boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        region_name=settings.s3_region,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key.get_secret_value(),
        config=Config(
            connect_timeout=settings.health_check_timeout_seconds,
            read_timeout=settings.health_check_timeout_seconds,
            retries={"mode": "standard", "total_max_attempts": 1},
            s3={"addressing_style": "path"},
        ),
    )
    client.head_bucket(Bucket=settings.s3_bucket)


DEPENDENCY_CHECKS: Mapping[str, DependencyCheck] = {
    "database": check_database,
    "redis": check_redis,
    "object_storage": check_object_storage,
}


def run_checks(settings: Settings, checks: Mapping[str, DependencyCheck]) -> dict[str, str]:
    """Run every check and report "ok" or "error" for each one. Never raises."""
    results: dict[str, str] = {}
    for name, check in checks.items():
        try:
            check(settings)
        except Exception:
            # Readiness must report failures, not crash. The full traceback goes to the logs.
            logger.warning("Readiness check failed: %s", name, exc_info=True)
            results[name] = "error"
        else:
            results[name] = "ok"
    return results
