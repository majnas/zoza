import pytest
from fastapi.testclient import TestClient
from app import app

# Pytest test function
def test_analyze_image():
    client = TestClient(app)
    image_url = "https://github.com/majnas/zoza/blob/master/zoza/asset/baby_and_birds.jpg?raw=true"
    response = client.post("/invoke", json={"image_url": image_url})
    assert response.status_code == 200
    assert "description" in response.json()
