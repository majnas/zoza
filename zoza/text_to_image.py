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


# class TextToImage:    
#     def __init__(self):
#         pass
#     def __call__(self, prompt: str):
#         result = (['https://scontent.fmel3-1.fna.fbcdn.net/o1/v/t0/f2/m340/AQNxsetgFipEi6FbRbgZxpALAdRKWI0BRahdJ2cJsnoC_grVCgX-eYawtOZVFp_lvTSSsYwkYHMSwOxxlO2iNbLmHDH-JftIPS-1iPwxui87u3SxoxrT03wa8AbfOduEbc1D74HPlVEHDX4eAYmswvpk5vw1.jpeg?_nc_ht=scontent.fmel3-1.fna.fbcdn.net&_nc_cat=106&ccb=9-4&oh=00_AYB-iHPP0ltuUocjCw_1Hay6piBRd2X4Zd40AbbVC-RQXw&oe=67BB23A9&_nc_sid=5b3566', 'https://scontent.fmel3-1.fna.fbcdn.net/o1/v/t0/f2/m340/AQMQ6JeQa81c9ZUK6rzSriDt7DgdBEPIl0MfDumZ3QoO3AdMFeAGpp4c4Cw4mO35SO_5NghwYKkvd94PPm2re2g_Lh8lGMcbJKtRYYwxtNx489h_vahzpWB46CM1JbJt3IPmqAVdj_NHi4kZmyEhmBMv7N4JOA.jpeg?_nc_ht=scontent.fmel3-1.fna.fbcdn.net&_nc_cat=110&ccb=9-4&oh=00_AYAmK4xEjUUFyPMHw5OUDk9SoAu8Y6fAalhF7vnjvgHM3w&oe=67BB2755&_nc_sid=5b3566', 'https://scontent.fmel3-1.fna.fbcdn.net/o1/v/t0/f2/m340/AQNUEOR0srKwYuYsEhBUOwRWxpxMORTcM40d6J50bR5cIwiGeNGHaHwlUBouRKmx7ObPvcl7F-ICqsWnX5GDo6hARl1Ajh-ntk1z60vlIuIhXGnwFY7zkiLHC_DOYwIaQ_PVb5_24wKAG3KWMgctF3QcyQI1hQ.jpeg?_nc_ht=scontent.fmel3-1.fna.fbcdn.net&_nc_cat=102&ccb=9-4&oh=00_AYA7qMnRXWdgr4ttbQksTnryycjv5zejUoFhx4TypW5ihQ&oe=67BB4585&_nc_sid=5b3566', 'https://scontent.fmel3-1.fna.fbcdn.net/o1/v/t0/f2/m340/AQPpyq6UmW9pILSQdPqulH2L8QHk2eTw3DGKwzBXcTod-iIhNwD6YiawGe_unV-CsuPEkIUf5Y9kcjgRPS3wh8jKZWrUKTQblpop4v7UKHMf6CGvkbtujcmStr9ZoEI-iuOu0go3d0fcKf697fwOTT9dHusZcw.jpeg?_nc_ht=scontent.fmel3-1.fna.fbcdn.net&_nc_cat=110&ccb=9-4&oh=00_AYCLeLB-czxcens_K_g3MLHPJtOkiuw2IMXDU4OgXcvVhw&oe=67BB4195&_nc_sid=5b3566'], ['https://scontent.fmel3-1.fna.fbcdn.net/o1/v/t0/f2/m257/AQPNDuVHFK9bbH1dHjaYrd04WtgtR1kG2xV6eQkfBlfqLhhoHjStTDeJnKsXTIvVCG2_DEHwlDkJHDrCtpZTfpUYUk_jqjS0B96ABxvSUo1UoTgysW4R7grfwQcF9g.mp4?_nc_ht=scontent.fmel3-1.fna.fbcdn.net&_nc_cat=110&ccb=9-4&oh=00_AYAgWVIMaQW6jqPTJa4dzRV5iJYMUb0rbrn6bzf_k7kI-g&oe=67BB18E4&_nc_sid=5b3566', 'https://scontent.fmel3-1.fna.fbcdn.net/o1/v/t0/f2/m248/AQMZ4eOgxE46kno_RvyhR5w2eE7Fqomgt8jtz6wu8x1bfRlZm_48PMXeLr8ieCabptrnTFFU72rHK1AUN9AHROXXwquhz7CiqE9Mnr5Eca8nvaSj43rTO12ZSHLPYA.mp4?_nc_ht=scontent.fmel3-1.fna.fbcdn.net&_nc_cat=102&ccb=9-4&oh=00_AYAklfoaMe-E46MR4Ac8yzjqelL_IoIMjvGDd_iCkA9Z4Q&oe=67BB3638&_nc_sid=5b3566', 'https://scontent.fmel3-1.fna.fbcdn.net/o1/v/t0/f2/m338/AQPw1tqBqTy7TpD3DGTQLjIwF55SW_bnmFTLFcNlW5QWhJpKfBbCeRRBHZsVlXWUjom8sZlZxirAteCITCAQPct5Gk0402CEYAoTZkz5tUcFbgUQe9DX49e5DmIxQ9ee.mp4?_nc_ht=scontent.fmel3-1.fna.fbcdn.net&_nc_cat=103&ccb=9-4&oh=00_AYA0xsbhKKuFOGs5rQIXoLttrxagLpCRHyU_UvmLGKURKg&oe=67BB34EB&_nc_sid=5b3566', 'https://scontent.fmel3-1.fna.fbcdn.net/o1/v/t0/f2/m253/AQMaiKrcGF1Dhtl1Oe-qF1n6_VEK_S-cP5nWpe6wv7fYNn0vDrR4IsvFilj2SqIUtTl8SuDxwx3x8F5ztDgi8uq23zKbjmS9YC9y2z7_hZPZM1HvXQaQUkn5CMta4GGJ.mp4?_nc_ht=scontent.fmel3-1.fna.fbcdn.net&_nc_cat=111&ccb=9-4&oh=00_AYBJJ3jFqD7wEfrf2M85d7ACDPQpZ7wJm16AiUUyX8Z0Ew&oe=67BB1813&_nc_sid=5b3566'])
#         return result


if __name__ == "__main__":
    # Example usage
    text_to_image = TextToImage.from_meta()
    # message = """
    # Imagine: Generate an image with following dscription. Image Description: The image shows a close-up of a golden dome with intricate patterns and a star at the top. There are three red flags with white text on them, fluttering in the wind. The building has blue and white tile work with arches and Arabic script. An air conditioning unit is visible on the right side of the building.
    # Object: The golden dome with the star at the top.
    # Color scheme: The image features a dominant gold color for the dome, with blue and white for the tile work, and red for the flags.
    # Background: The background is a clear blue sky, indicating a sunny day.
    # """

    message = """
    The image shows a baby sitting in a bathtub filled with bubbles. The baby has curly hair and is smiling, with a joyful expression on their face. The background features a patterned wall and some bottles, suggesting a bathroom setting
    """

    message = """
    Image Description: The image features a baby sitting on the ground, surrounded by a group of small birds. The baby is smiling broadly, appearing happy and content. The birds are perched on the baby's head, shoulders, and hands, creating a playful and whimsical scene.
    Object: The dominant object in the image is the baby.
    Color scheme: The image has a soft, pastel color scheme with shades of white, beige, and light brown. The birds have a mix of white, gray, and black feathers.
    Background: The background is a blurred, natural setting with hints of greenery and pink flowers, suggesting an outdoor environment, possibly a garden or park.
    """

    # message = """
    # Imagine: A big ball.
    # """
    # result {'message': '\n', 'sources': [], 'media': [{'url': '', 'type': 'IMAGE', 'prompt': ''}, {'url': '', 'type': 'IMAGE', 'prompt': ''}]}

    image_urls, video_urls = text_to_image(prompt=message)
    ic(image_urls, video_urls)





