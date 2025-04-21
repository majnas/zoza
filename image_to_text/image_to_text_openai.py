from openai import OpenAI
import os
import json
from icecream import ic
from typing import List, Dict

class ImageToTextOpenAI:
    def __init__(self, model: str, api_key: str):
        """
        Initialize the ImageToWanCmd class with a specified model and API key.
        
        Args:
            model (str): The OpenAI model to use (e.g., 'gpt-4o-mini').
            api_key (str): The API key for authentication. Defaults to 'OPENAI_API_KEY'.
                          If set to 'OPENAI_API_KEY', it will try to fetch from environment variables.
        """
        if not api_key:
            raise ValueError("API key not provided and not found in environment variables.")
        
        self.model = model  # Store model name as string
        self.client = OpenAI(api_key=api_key)

    @property
    def image_to_text_format(self, action_list: List[str]) -> str:
        base = (
            "I want to generate a vibrant and dynamic videos using the given image and a Large Vision Model. "
            "The videos should be visually engaging and rich in detail. For each given action create a prompt for the video based on following requirements. "
            "High Detail & Realism: Preserve intricate textures and visual elements from the image. "
            "Energy & Vibrancy: Use dynamic movement, rich colors, and smooth transitions. "
            "Cinematic Quality: Apply effects like depth of field, natural lighting, and camera movements. Smooth Scene Progression: Ensure logical and fluid storytelling without abrupt changes. "
            "Natural Motion & Interaction: Any movements should feel organic and visually coherent. "
            "High-Quality Rendering: Avoid jitter, maintain consistency, and output in high resolution. "
            "Please generate a visually compelling video based on these guidelines. "
            "Do not itemize the prompt. "
            "Write in single paragraph. "
            "Do not use special characters.\n\n"
            "["
        )

        # build one JSON-like entry per action
        entries = [
            '{{"Action": "{action}", "Prompt": ?}}'.format(action=action)
            for action in action_list
        ]

        # join them with commas and close the array
        return base + ", ".join(entries) + "]"


    def analyze_image(self, image_url: str, action_list: List[str]) -> List[Dict[str, str]]:
        """
        Generate video-prompt text based on an image URL and a list of actions.

        This sends the image and the actions off to the LLM, which returns
        a JSON array of two objects, each containing:
          - "Action": the original action description
          - "Prompt" : the LLM-generated video prompt text

        Args:
            image_url (str): URL of the image to process.
            action_list (List[str]): A list of action descriptions to turn
                                     into video prompts.

        Returns:
            List[Dict[str, str]]: A list of two dicts, each with exactly the
                                  keys "Action" and "Prompt".

        Raises:
            Exception: If the API call fails or the response cannot be
                       parsed into valid JSON.
        """
        SYSTEM = """You are a helpful assistant.  
When you answer, output **only** a JSON array with two objects, each with exactly these keys:

[
  {
    "Action": "<the action description>",
    "Prompt":  "<the generated prompt text>"
  },
  {
    "Action": "<the action description>",
    "Prompt":  "<the generated prompt text>"
  }
]

Do not emit any extra text, markdown, or comments—just valid JSON."""
        
        messages = [
            {"role": "system",  "content": SYSTEM},
            {"role": "user",    "content": self.image_to_text_format(action_list)},
            {"role": "user",    "content": "", "image_url": {"url": image_url}}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            content = response.choices[0].message.content
            content_json = json.loads(content)
            return content_json
        except Exception as e:
            raise Exception(f"Error generating text from image URL: {e}")
        


# Example usage
if __name__ == "__main__":
    model_ = "gpt-4o-mini"
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    image_url_ = "https://raw.githubusercontent.com/majnas/zoza/refs/heads/master/image_to_text/asset/ZOZA.webp"
    analyzer = ImageToTextOpenAI(model=model_, api_key=OPENAI_API_KEY)
    response = analyzer.analyze_image(image_url_)
    print(response)
