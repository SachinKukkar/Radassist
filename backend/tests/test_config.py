import pytest
from pydantic import SecretStr, ValidationError

from app.core.config import Settings

PROD_DATABASE_URL = SecretStr("postgresql://app:real-password@db.internal:5432/radassist")


def test_development_accepts_default_credentials() -> None:
    settings = Settings(_env_file=None, environment="development")

    assert settings.s3_bucket == "radassist-images"


def test_production_rejects_default_database_url() -> None:
    with pytest.raises(ValidationError, match="RADASSIST_DATABASE_URL"):
        Settings(_env_file=None, environment="production")


def test_production_rejects_default_s3_secret() -> None:
    with pytest.raises(ValidationError, match="RADASSIST_S3_SECRET_KEY"):
        Settings(_env_file=None, environment="production", database_url=PROD_DATABASE_URL)


def test_production_accepts_real_credentials() -> None:
    settings = Settings(
        _env_file=None,
        environment="production",
        database_url=PROD_DATABASE_URL,
        s3_secret_key=SecretStr("a-real-secret-from-a-secret-manager"),
    )

    assert settings.environment == "production"


def test_secrets_are_hidden_when_printed() -> None:
    settings = Settings(_env_file=None)

    assert "radassist-dev-secret" not in repr(settings)
    assert str(settings.s3_secret_key) == "**********"
