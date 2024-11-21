from typing import Any, Generator
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from api.main import app


@pytest.fixture(scope="session")
def test_client() -> Generator[TestClient, Any, None]:
    with TestClient(app, base_url="http://testserver/api/v1") as client:
        yield client


@pytest.fixture(scope="function")
def test_product_id(test_client) -> Generator[UUID, Any, None]:
    product_id = uuid4()
    test_client.post(
        "/products",
        json={
            "id": str(product_id),
            "name": "Tablet",
            "description": "12.9, 10000 mAh",
        },
    )
    yield product_id
    # if not testing in a container
    test_client.delete(f"/products/{product_id}")
