"""Container health check: `python -m app.healthcheck` exits 0 if /health/live returns 200."""

import http.client
import sys


def main(host: str = "127.0.0.1", port: int = 8000, timeout: float = 2.0) -> int:
    """Return 0 if the liveness endpoint answers 200, otherwise 1."""
    connection = http.client.HTTPConnection(host, port, timeout=timeout)
    try:
        connection.request("GET", "/health/live")
        return 0 if connection.getresponse().status == 200 else 1
    except OSError:
        return 1
    finally:
        connection.close()


if __name__ == "__main__":
    sys.exit(main())
