import pytest
from fastapi.testclient import TestClient
from app import app

# Pytest test function
def test_analyze_image():
    client = TestClient(app)
    image_url = "https://raw.githubusercontent.com/majnas/zoza/refs/heads/master/image_to_text/asset/baby_and_birds.jpg"
    response = client.post("/invoke", json={"image_url": image_url})
    assert response.status_code == 200
    assert "description" in response.json()


import pytest
from fastapi.testclient import TestClient
from app import app

# Fixture for TestClient
@pytest.fixture
def client():
    return TestClient(app)

# Test for /invoke endpoint (existing test)
def test_analyze_image(client):
    image_url = "https://raw.githubusercontent.com/majnas/zoza/refs/heads/master/image_to_text/asset/baby_and_birds.jpg"
    response = client.post("/invoke", json={"image_url": image_url})
    assert response.status_code == 200
    assert "description" in response.json()

# Test for /IMAGE_TO_TEXT/generate-bash endpoint with default behavior
def test_generate_bash_default(client):
    image_url = "https://raw.githubusercontent.com/majnas/zoza/refs/heads/master/image_to_text/asset/baby_and_birds.jpg"
    response = client.post("/IMAGE_TO_TEXT/generate-bash", json={"image_url": image_url})
    
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
    response_json = response.json()
    assert "bash_command" in response_json, "Response should contain 'bash_command' key"
    
    bash_command = response_json["bash_command"]
    assert isinstance(bash_command, str), "Bash command should be a string"
    assert "curl" in bash_command, "Bash command should include curl for downloading"
    assert "torchrun" in bash_command, "Bash command should include torchrun for generation"
    assert image_url in bash_command, "Bash command should include the provided image URL"
    
    print("Generated Bash Command (Default):")
    print(bash_command)

# Test for /IMAGE_TO_TEXT/generate-bash endpoint error handling
def test_generate_bash_invalid_input(client):
    # Test with missing image_url
    response = client.post("/IMAGE_TO_TEXT/generate-bash", json={})
    
    assert response.status_code == 422, f"Expected status 422 for invalid input, got {response.status_code}"
    response_json = response.json()
    assert "detail" in response_json, "Response should contain error details"
    print("\nError Response (Missing image_url):")
    print(response_json)

# Test for /IMAGE_TO_TEXT/generate-bash endpoint with unreachable image
def test_generate_bash_unreachable_image(client):
    image_url = "https://nonexistent.example.com/image.jpg"
    response = client.post("/IMAGE_TO_TEXT/generate-bash", json={"image_url": image_url})
    
    # Depending on how ImageToTextWan handles unreachable URLs, this could be 200 or 500
    assert response.status_code in [200, 500], f"Unexpected status code: {response.status_code}"
    response_json = response.json()
    
    if response.status_code == 200:
        assert "bash_command" in response_json, "Response should contain 'bash_command' key"
        bash_command = response_json["bash_command"]
        assert image_url in bash_command, "Bash command should include the unreachable URL"
        print("\nGenerated Bash Command (Unreachable Image):")
        print(bash_command)
    else:
        assert "detail" in response_json, "Response should contain error details"
        print("\nError Response (Unreachable Image):")
        print(response_json)