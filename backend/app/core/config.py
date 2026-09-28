from functools import lru_cache
from typing import Literal, Self

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Local-development defaults. They match compose.yaml, so `make up` works without any setup.
# Production must override them: see Settings.forbid_dev_secrets_in_production.
DEV_DATABASE_URL = "postgresql://radassist:radassist@localhost:5432/radassist"
# Not a real secret: a well-known local default that production refuses to accept.
DEV_S3_SECRET_KEY = "radassist-dev-secret"  # noqa: S105


class Settings(BaseSettings):
    """Application settings, loaded from environment variables prefixed with RADASSIST_.

    Values are read from the real environment first, then from a local .env file.
    """

    model_config = SettingsConfigDict(
        env_prefix="RADASSIST_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Application ---
    app_name: str = "RadAssist API"
    environment: Literal["development", "test", "production"] = "development"
    debug: bool = False
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    log_json: bool = False
    api_v1_prefix: str = "/api/v1"

    # --- PostgreSQL ---
    database_url: SecretStr = SecretStr(DEV_DATABASE_URL)

    # --- Redis ---
    redis_url: str = "redis://localhost:6379/0"

    # --- S3-compatible object storage ---
    s3_endpoint_url: str = "http://localhost:8333"
    s3_region: str = "us-east-1"
    s3_access_key: str = "radassist"
    s3_secret_key: SecretStr = SecretStr(DEV_S3_SECRET_KEY)
    s3_bucket: str = "radassist-images"

    # --- Health checks ---
    health_check_timeout_seconds: float = Field(default=2.0, gt=0, le=10)

    @model_validator(mode="after")
    def forbid_dev_secrets_in_production(self) -> Self:
        """Refuse to start in production with the well-known development credentials."""
        if self.environment != "production":
            return self
        if self.database_url.get_secret_value() == DEV_DATABASE_URL:
            raise ValueError("RADASSIST_DATABASE_URL must be set in production")
        if self.s3_secret_key.get_secret_value() == DEV_S3_SECRET_KEY:
            raise ValueError("RADASSIST_S3_SECRET_KEY must be set in production")
        return self


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance so the environment is parsed only once."""
    return Settings()
