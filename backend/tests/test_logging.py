import json
import logging

from app.core.logging import JsonFormatter


def test_json_formatter_produces_valid_json() -> None:
    record = logging.LogRecord(
        name="radassist.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="hello %s",
        args=("world",),
        exc_info=None,
    )

    output = json.loads(JsonFormatter().format(record))

    assert output["message"] == "hello world"
    assert output["level"] == "INFO"
    assert output["logger"] == "radassist.test"
    assert "timestamp" in output
