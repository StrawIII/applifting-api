from fastapi import status


def test_create_product(test_client):
    response = test_client.post(
        "/api/v1/products",
        json={"name": "Tablet", "description": "12.9, 10000 mAh"},
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == ...


def test_update_product(test_client): ...


def test_delete_product(test_client): ...


def test_create_product_conflict(): ...
