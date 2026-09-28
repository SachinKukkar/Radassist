from app.healthcheck import main


def test_healthcheck_fails_when_api_is_unreachable() -> None:
    # Nothing listens on port 9 on a normal machine, so the connection is refused.
    assert main(port=9, timeout=0.5) == 1
