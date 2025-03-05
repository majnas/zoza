import pytest
from fastapi.testclient import TestClient
from app import app  # Import the FastAPI app from app.py

client = TestClient(app)

def test_generate_text_to_image():
    message = """
    Image Description: The image features a baby sitting on the ground, surrounded by a group of small birds. The baby is smiling broadly, appearing happy and content. The birds are perched on the baby's head, shoulders, and hands, creating a playful and whimsical scene.
    Object: The dominant object in the image is the baby.
    Color scheme: The image has a soft, pastel color scheme with shades of white, beige, and light brown. The birds have a mix of white, gray, and black feathers.
    Background: The background is a blurred, natural setting with hints of greenery and pink flowers, suggesting an outdoor environment, possibly a garden or park.
    """
    response = client.post("/invoke/", json={"prompt": message})
    assert response.status_code == 200
    data = response.json()
    assert "image_urls" in data
    assert "video_urls" in data
    assert isinstance(data["image_urls"], list)
    assert isinstance(data["video_urls"], list)
    assert all(isinstance(url, str) for url in data["image_urls"])
    assert all(isinstance(url, str) for url in data["video_urls"])
