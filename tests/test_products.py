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


def test_create_and_update_product(test_client):
    product_id = uuid4()
    test_client.post(
        "/api/v1/products",
        json={
            "id": str(product_id),
            "name": "Tablet",
            "description": "12.9, 10000 mAh",
        },
    )
    response = test_client.put(
        f"/api/v1/products/{product_id}",
        json={"name": "iPad", "description": "11.5, 9000 mAh"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "name": "iPad",
        "description": "11.5, 9000 mAh",
    }


def test_delete_product(test_client):
    product_id = uuid4()
    test_client.post(
        "/api/v1/products",
        json={
            "id": str(product_id),
            "name": "Tablet",
            "description": "12.9, 10000 mAh",
        },
    )
    response = test_client.delete(f"/api/v1/products/{product_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"id": str(product_id)}


# def test_create_product_id_conflict(test_client):
#     product_id = uuid4()
#     test_client.post(
#         "/api/v1/products",
#         json={
#             "id": str(product_id),
#             "name": "Tablet",
#             "description": "12.9, 10000 mAh",
#         },
#     )
#     response = test_client.post(
#         "/api/v1/products",
#         json={
#             "id": str(product_id),
#             "name": "Tablet",
#             "description": "12.9, 10000 mAh",
#         },
#     )
#     assert response.status_code == status.HTTP_201_CREATED
#     assert response.json()["id"] != str(product_id)
#     assert response.json()["name"] == "Tablet"
#     assert response.json()["description"] == "12.9, 10000 mAh"
