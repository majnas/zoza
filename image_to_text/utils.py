import tempfile
from pathlib import Path
import requests

def download_image_by_url(image_url: str) -> str:
    """
    Download an image from a URL and save it to a persistent temporary file.
    
    :param image_url: The URL of the image to download.
    :return: The file path of the downloaded image as a string, which persists until manually deleted.
    :raises requests.exceptions.RequestException: If the download fails.
    """
    print("image_url", image_url)
    
    # Create a named temporary file that persists after the function
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    image_path = temp_file.name
    temp_file.close()  # Close the file handle so we can write to it

    # Download the image from the URL
    response = requests.get(image_url, stream=True)
    response.raise_for_status()  # Raise an error for bad HTTP status codes

    # Write the image to the temporary file
    with open(image_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:  # Filter out keep-alive chunks
                f.write(chunk)
    
    return image_path

# Example usage
if __name__ == "__main__":
    url = "https://raw.githubusercontent.com/majnas/zoza/refs/heads/master/image_to_text/asset/baby_and_birds.jpg"
    try:
        path = download_image_by_url(url)
        print(f"Image downloaded to: {path}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading image: {e}")