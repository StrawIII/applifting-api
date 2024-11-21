from uuid import uuid4

from fastapi import status


def test_create_product(test_client):
    product_id = uuid4()
    response = test_client.post(
        "/api/v1/products",
        json={
            "id": str(product_id),
            "name": "Tablet",
            "description": "12.9, 10000 mAh",
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        "id": str(product_id),
        "name": "Tablet",
        "description": "12.9, 10000 mAh",
    }
    test_client.delete(f"/api/v1/products/{product_id}")


def test_create_product_duplicate(test_client, test_product_id):
    response = test_client.post(
        "/api/v1/products",
        json={
            "id": str(test_product_id),
            "name": "Tablet",
            "description": "12.9, 10000 mAh",
        },
    )
    assert response.status_code == status.HTTP_409_CONFLICT


def test_create_product_invalid_query(test_client):
    product_id = 1
    response = test_client.post(
        "/api/v1/products",
        json={
            "id": str(product_id),
            "name": "Tablet",
            "description": "12.9, 10000 mAh",
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_product_invalid_body(test_client):
    product_id = uuid4()
    response = test_client.post(
        "/api/v1/products",
        json={
            "id": str(product_id),
            "name": "Tablet",
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_read_product(test_client, test_product_id):
    response = test_client.delete(f"/api/v1/products/{test_product_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == str(test_product_id)


def test_read_product_nonexistent(test_client):
    product_id = uuid4()
    response = test_client.delete(f"/api/v1/products/{product_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Product not found"


def test_read_product_invalid_query(test_client):
    product_id = 1
    response = test_client.delete(f"/api/v1/products/{product_id}")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_update_product(test_client, test_product_id):
    response = test_client.put(
        f"/api/v1/products/{test_product_id}",
        json={"name": "iPad", "description": "11.5, 9000 mAh"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "name": "iPad",
        "description": "11.5, 9000 mAh",
    }


def test_update_product_nonexistent(test_client):
    product_id = uuid4()
    response = test_client.put(
        f"/api/v1/products/{product_id}",
        json={"name": "iPad", "description": "11.5, 9000 mAh"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Product not found"


def test_update_product_invalid_query(test_client):
    product_id = 1
    response = test_client.put(
        f"/api/v1/products/{product_id}",
        json={"name": "iPad", "description": "11.5, 9000 mAh"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_update_product_invalid_body(test_client, test_product_id):
    response = test_client.put(
        f"/api/v1/products/{test_product_id}",
        json={
            "name": "iPad",
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_delete_product(test_client, test_product_id):
    response = test_client.delete(f"/api/v1/products/{test_product_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"id": str(test_product_id)}


def test_delete_product_nonexistent(test_client):
    product_id = uuid4()
    response = test_client.delete(f"/api/v1/products/{product_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Product not found"


def test_delete_product_invalid_query(test_client):
    product_id = 1
    response = test_client.delete(f"/api/v1/products/{product_id}")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
