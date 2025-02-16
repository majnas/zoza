from meta_ai_api import MetaAI
from pathlib import Path
from dotenv import load_dotenv
import os
from rich import print
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
    
    def __call__(self, message: str):
        """
        Generate an image based on the given message prompt.
        """
        response = self.ai.prompt(message=message)
        return response  # Assuming response is already in JSON format

if __name__ == "__main__":
    # Example usage
    text_to_image = TextToImage.from_meta()
    message = """
    Imagine: This image features a heartwarming scene of a baby surrounded by several small birds.
    In the center of the frame is a baby with a bright, joyful smile, showing a few baby teeth. The baby has fair skin, round cheeks, and dark hair. They are wearing a diaper, suggesting a youthful age. The baby is looking directly forward with a very happy and engaged expression. Their arms are outstretched, and they seem to be gently holding or interacting with one of the birds perched on their hand.
    Around the baby are six small, white birds with grey wings and yellow beaks. These birds are perched on different parts of the baby: one is on the baby's head, one is on the baby's left shoulder, one on the right shoulder, one on the left hand, one on the right arm, and one near the baby’s right leg. The birds are all facing different directions, some towards the baby and some away. They appear calm and unafraid, adding to the gentle and peaceful atmosphere of the picture.
    The background is softly blurred, indicating a shallow depth of field which keeps the focus on the baby and the birds. Hints of greenery and out-of-focus pink blossoms suggest an outdoor setting, perhaps a garden or a natural environment. The lighting in the image appears soft and natural, highlighting the baby's and birds' features without harsh shadows.
    Overall, the image conveys a sense of innocence, joy, and harmony between nature and childhood. The baby's happy expression and the presence of the birds create a tender and delightful scene.
    """
    # result {'message': '\n', 'sources': [], 'media': [{'url': '', 'type': 'IMAGE', 'prompt': ''}, {'url': '', 'type': 'IMAGE', 'prompt': ''}]}

    result = text_to_image(message=message)
    if result:
        for m in result.get("media", []):
            print(m['url'])






