import os
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

class ImageToText:
    def __init__(self, model: str, api_key_env: str = 'OPENROUTER_API_KEY'):
        """
        Initialize the ImageToText with a specific model and API key.
        :param model: The model to use for analysis.
        :param api_key_env: The environment variable storing the API key.
        """
        dotenv_path = Path(__file__).resolve().parent.parent / ".env"
        load_dotenv(dotenv_path=dotenv_path)
        
        self.api_key = os.getenv(api_key_env)
        if not self.api_key:
            raise ValueError("API key not found in environment variables.")
        
        self.model = model
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
        )

    def analyze_image(self, image_url: str, text: str) -> str:
        """
        Analyze an image using the model and return the response.
        :param image_url: URL of the image to analyze.
        :return: Model's response describing the image.
        """
        completion = self.client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "<YOUR_SITE_URL>",  # Optional
                "X-Title": "<YOUR_SITE_NAME>",  # Optional
            },
            extra_body={},
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": text},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ]
                }
            ]
        )
        return completion.choices[0].message.content

# Example Usage
if __name__ == "__main__":
    model_ = "qwen/qwen-vl-plus:free"
    image_url_ = "https://github.com/majnas/zoza/blob/master/zoza/asset/baby_and_birds.jpg?raw=true"
    image_to_text_format = """
    "Describe the image based on following format."
    'Image Description: Put long description of the image in here'
    'Object: Put the name of dominant object in image here'
    'Color scheme: Put color scheme of image here'
    'Background: Put short description of the image background here'
    """
    analyzer = ImageToText(model_)
    response = analyzer.analyze_image(image_url_, text=image_to_text_format)
    print(response)
