from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client() -> Iterator[TestClient]:
    """A test client bound to a fresh app; the `with` block runs startup/shutdown."""
    with TestClient(create_app()) as test_client:
        yield test_client
