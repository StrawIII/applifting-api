from fastapi import status


def test_health(test_client):
    response = test_client.get("/health")
    assert response.status_code == status.HTTP_204_NO_CONTENT
