from typing import Any, Generator

import pytest
from fastapi.testclient import TestClient

from api.main import app


@pytest.fixture(scope="session")
def test_client() -> Generator[TestClient, Any, None]:
    with TestClient(app) as client:
        yield client
