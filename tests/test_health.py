from fastapi import status


def test_health(test_client):
    response = test_client.get("/api/v1/health")
    assert response.status_code == status.HTTP_204_NO_CONTENT
