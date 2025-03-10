from openai import OpenAI
import os

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
    def image_to_text_format(self):
        """
        Default prompt format for generating vibrant and dynamic video descriptions.
        
        Returns:
            str: The default prompt string.
        """
        return """I want to generate a vibrant and dynamic video using the following image and a Large Vision Model. The video should be visually engaging and rich in detail. Create a prompt for the video based on following requirements. High Detail & Realism: Preserve intricate textures and visual elements from the image. Energy & Vibrancy: Use dynamic movement, rich colors, and smooth transitions. Cinematic Quality: Apply effects like depth of field, natural lighting, and camera movements. Smooth Scene Progression: Ensure logical and fluid storytelling without abrupt changes. Natural Motion & Interaction: Any movements should feel organic and visually coherent. High-Quality Rendering: Avoid jitter, maintain consistency, and output in high resolution. Please generate a visually compelling video based on these guidelines. Do not itemize the prompt. Write in single paragraph. Do not use special charecters."""

    def analyze_image(self, image_url: str) -> str:
        """
        Generate text based on an image URL and a prompt.
        
        Args:
            image_url (str): URL of the image to process.
        
        Returns:
            str: The generated text response from the model.
        """

        # Prepare the message content in the format expected by OpenAI API
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": self.image_to_text_format},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            }
        ]
        
        try:
            # Call the OpenAI API directly
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error generating text from image URL: {e}")


# Example usage
if __name__ == "__main__":
    model_ = "gpt-4o-mini"
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    image_url_ = "https://raw.githubusercontent.com/majnas/zoza/refs/heads/master/image_to_text/asset/baby_and_birds.jpg"
    analyzer = ImageToTextOpenAI(model=model_, api_key=OPENAI_API_KEY)
    response = analyzer.analyze_image(image_url_)
    print(response)
