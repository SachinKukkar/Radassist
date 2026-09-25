import json
import logging
import logging.config
from datetime import UTC, datetime
from typing import Any

PLAIN_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"


class JsonFormatter(logging.Formatter):
    """Render each log record as one line of JSON, which log aggregators can parse."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def setup_logging(level: str = "INFO", json_logs: bool = False) -> None:
    """Configure the root logger and route uvicorn's loggers through it."""
    config: dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "plain": {"format": PLAIN_FORMAT},
            "json": {"()": JsonFormatter},
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "json" if json_logs else "plain",
            },
        },
        "root": {"handlers": ["console"], "level": level},
        "loggers": {
            # Remove uvicorn's own handlers so its logs use our format too.
            "uvicorn": {"handlers": [], "propagate": True},
            "uvicorn.error": {"handlers": [], "propagate": True},
            "uvicorn.access": {"handlers": [], "propagate": True},
        },
    }
    logging.config.dictConfig(config)
