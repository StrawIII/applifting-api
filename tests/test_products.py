from uuid import uuid4

from fastapi import status


def test_read_catalogue(test_client):
    response = test_client.get("/products/catalogue")
    assert response.status_code == status.HTTP_200_OK


def test_read_products(test_client):
    response = test_client.get("/products")
    assert response.status_code == status.HTTP_200_OK


def test_create_product(test_client):
    product_id = uuid4()
    request_body = {
        "id": str(product_id),
        "name": "Tablet",
        "description": "12.9, 10000 mAh",
    }
    response = test_client.post("/products", json=request_body)
    response_body = response.json()
    try:
        assert response.status_code == status.HTTP_201_CREATED
        assert response_body["id"] == request_body["id"]
        assert response_body["name"] == request_body["name"]
        assert response_body["description"] == response_body["description"]
    finally:
        test_client.delete(f"/products/{product_id}")


def test_create_product_duplicate(test_client, test_product_id):
    request_body = {
        "id": str(test_product_id),
        "name": "Tablet",
        "description": "12.9, 10000 mAh",
    }
    response = test_client.post("/products", json=request_body)
    assert response.status_code == status.HTTP_409_CONFLICT


def test_create_product_invalid_query(test_client):
    product_id = 1
    request_body = {
        "id": str(product_id),
        "name": "Tablet",
        "description": "12.9, 10000 mAh",
    }
    response = test_client.post("/products", json=request_body)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_product_invalid_body(test_client):
    product_id = uuid4()
    request_body = {
        "id": str(product_id),
        "name": "Tablet",
    }
    response = test_client.post("/products", json=request_body)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_read_product(test_client, test_product_id):
    response = test_client.delete(f"/products/{test_product_id}")
    response_body = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert response_body["id"] == str(test_product_id)


def test_read_product_nonexistent(test_client):
    product_id = uuid4()
    response = test_client.delete(f"/products/{product_id}")
    response_body = response.json()
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response_body["detail"] == "Product not found"


def test_read_product_invalid_query(test_client):
    product_id = 1
    response = test_client.delete(f"/products/{product_id}")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_update_product(test_client, test_product_id):
    request_body = {"name": "iPad", "description": "11.5, 9000 mAh"}
    response = test_client.put(f"/products/{test_product_id}", json=request_body)
    response_body = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert response_body["id"] == str(test_product_id)
    assert response_body["name"] == request_body["name"]
    assert response_body["description"] == request_body["description"]


def test_update_product_nonexistent(test_client):
    product_id = uuid4()
    request_body = {"name": "iPad", "description": "11.5, 9000 mAh"}
    response = test_client.put(f"/products/{product_id}", json=request_body)
    response_body = response.json()
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response_body["detail"] == "Product not found"


def test_update_product_invalid_query(test_client):
    product_id = 1
    request_body = {"name": "iPad", "description": "11.5, 9000 mAh"}
    response = test_client.put(f"/products/{product_id}", json=request_body)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_update_product_invalid_body(test_client, test_product_id):
    request_body = {"name": "iPad"}
    response = test_client.put(f"/products/{test_product_id}", json=request_body)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_delete_product(test_client, test_product_id):
    response = test_client.delete(f"/products/{test_product_id}")
    response_body = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert response_body == {"id": str(test_product_id)}


def test_delete_product_nonexistent(test_client):
    product_id = uuid4()
    response = test_client.delete(f"/products/{product_id}")
    response_body = response.json()
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response_body["detail"] == "Product not found"


def test_delete_product_invalid_query(test_client):
    product_id = 1
    response = test_client.delete(f"/products/{product_id}")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
