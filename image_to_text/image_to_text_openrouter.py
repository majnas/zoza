import os
from pathlib import Path
from openai import OpenAI

class ImageToTextOpenRouter:
    def __init__(self, model: str, api_key: str):
        """
        Initialize the ImageToText with a specific model and API key.
        :param model: The model to use for analysis.
        :param api_key_env: The environment variable storing the API key.
        """ 
        if not api_key:
            raise ValueError("API key not provided and not found in environment variables.")

        self.model = model
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )        

    @property
    def image_to_text_format(self):
        image_to_text_format = """
        "Describe the image based on following format."
        'Image Description: Put long description of the image in here'
        'Object: Put the name of dominant object in image here'
        'Color scheme: Put color scheme of image here'
        'Background: Put short description of the image background here'
        """

        # image_to_text_format = """
        # "Describe the image in detail using the following format. Strictly follow the template and do not include labels like 'Image Description:', 'Object:', 'Color scheme:', or 'Background:' in your response. Only provide the content for each section as described below."
        # 'Put a long and detailed description of the image here, covering all visible elements, actions, and context.'
        # 'Put the name of the dominant object(s) in the image here, along with their appearance, position, and notable features.'
        # 'Put the overall color scheme of the image here, including dominant colors, contrasts, and any notable color patterns or tones.'
        # 'Put a detailed description of the background here, including its setting, elements, and how it relates to the main objects.'
        # """
        return image_to_text_format

    def analyze_image(self, image_url: str) -> str:
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
                        {"type": "text", "text": self.image_to_text_format},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ]
                }
            ]
        )
        return completion.choices[0].message.content


# Example Usage
if __name__ == "__main__":
    model_ = "qwen/qwen-vl-plus:free"
    image_url_ = "https://raw.githubusercontent.com/majnas/zoza/refs/heads/master/image_to_text/asset/baby_and_birds.jpg"
    analyzer = ImageToTextOpenRouter(model_)
    response = analyzer.analyze_image(image_url_)
    print(response)
