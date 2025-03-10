import os
from pathlib import Path
import ollama

class ImageToTextOllama:
    def __init__(self, model: str):
        """
        Initialize the ImageToTextOllama with a specific model and host URL.
        :param model: The model to use for analysis (e.g., granite3.2-vision:2b).
        :param host: The base URL for the Ollama server.
        """
        self.model = model
        self.client = ollama

    @property
    def image_to_text_format(self):
        """
        Define the format for image description output.
        """
        image_to_text_format = """
        "Describe the image based on following format."
        'Image Description: Put long description of the image in here'
        'Object: Put the name of dominant object in image here'
        'Color scheme: Put color scheme of image here'
        'Background: Put short description of the image background here'
        """
        return image_to_text_format

    def analyze_image(self, image_path: str) -> str:
        """
        Analyze an image using the model and return the response.
        :param image_path: Local file path of the image to analyze.
        :return: Model's response describing the image.
        """
        # Ensure the image path exists
        if not Path(image_path).exists():
            raise FileNotFoundError(f"Image file not found at: {image_path}")

        # Perform the chat request with Ollama
        response = self.client.chat(
            model=self.model,
            messages=[
                {
                    'role': 'user',
                    'content': self.image_to_text_format,
                    'images': [image_path]
                }
            ]
        )
        return response['message']['content']


# Example Usage
if __name__ == "__main__":
    model_ = "granite3.2-vision:2b"
    image_path_ = "./asset/baby_and_birds.jpg"
    analyzer = ImageToTextOllama(model_)
    response = analyzer.analyze_image(image_path_)
    print(response)
