from meta_ai_api import MetaAI
from pathlib import Path
from dotenv import load_dotenv
import os
from icecream import ic

class TextToImage:
    @classmethod
    def from_meta(cls):
        """
        Initialize the MetaAI instance using environment variables and return a TextToImage instance.
        """
        # Load environment variables from .env file
        dotenv_path = Path(__file__).resolve().parent.parent / ".env"
        load_dotenv(dotenv_path=dotenv_path)
        
        # Retrieve Facebook credentials from environment variables
        fb_email = os.getenv("FACEBOOK_EMAIL")
        fb_password = os.getenv("FACEBOOK_PASSWORD")
        
        if not fb_email or not fb_password:
            raise ValueError("Facebook email and password must be set in the .env file")
        
        # Initialize MetaAI with the credentials
        ai = MetaAI(fb_email=fb_email, fb_password=fb_password)

        # Return an instance of TextToImage
        return cls(ai)
    
    def __init__(self, ai: MetaAI):
        self.ai = ai
    
    def __call__(self, prompt: str):
        """
        Generate an image based on the given message prompt.
        """
        imagine_prompt = f"Imagine: Generate an image with following dscription. {prompt}"
        imagine_result = self.ai.prompt(imagine_prompt)
        # imagine_result {'message': '\n', 'sources': [], 'media': [{'url': '', 'type': 'IMAGE', 'prompt': ''}, {'url': '', 'type': 'IMAGE', 'prompt': ''}]}
        image_urls = []
        if imagine_result:
            for m in imagine_result.get("media", []):
                if m['type'] == 'IMAGE':
                    image_urls.append(m['url'])

        animate_prompt = f"Animate: Generate an image with following dscription. {prompt}"
        animate_result = self.ai.prompt(animate_prompt)
        video_urls = []
        if animate_result:
            for m in animate_result.get("media", []):
                if m['type'] == 'VIDEO':
                    video_urls.append(m['url'])

        return image_urls, video_urls


if __name__ == "__main__":
    # Example usage
    text_to_image = TextToImage.from_meta()
    message = """
    Imagine: Generate an image with following dscription. Image Description: The image shows a close-up of a golden dome with intricate patterns and a star at the top. There are three red flags with white text on them, fluttering in the wind. The building has blue and white tile work with arches and Arabic script. An air conditioning unit is visible on the right side of the building.
    Object: The golden dome with the star at the top.
    Color scheme: The image features a dominant gold color for the dome, with blue and white for the tile work, and red for the flags.
    Background: The background is a clear blue sky, indicating a sunny day.
    """

    # message = """
    # Imagine: A big ball.
    # """
    # result {'message': '\n', 'sources': [], 'media': [{'url': '', 'type': 'IMAGE', 'prompt': ''}, {'url': '', 'type': 'IMAGE', 'prompt': ''}]}

    image_urls, video_urls = text_to_image(prompt=message)
    ic(image_urls, video_urls)




