from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
import os

class ImageToTextWan:
    def __init__(self, model: str, api_key: str = 'OPENROUTER_API_KEY'):
        """
        Initialize the ImageToTextWan class with a specified model and API key.
        
        Args:
            model (str): The OpenAI model to use (e.g., 'gpt-4o-mini').
            api_key (str): The API key for authentication. Defaults to 'OPENROUTER_API_KEY'.
                          If set to 'OPENROUTER_API_KEY', it will try to fetch from environment variables.
        """
        if api_key == 'OPENROUTER_API_KEY':
            self.api_key = os.getenv('OPENROUTER_API_KEY') or os.getenv('OPENAI_API_KEY')
            if not self.api_key:
                raise ValueError("API key not provided and not found in environment variables.")
        else:
            self.api_key = api_key
        
        self.model = ChatOpenAI(model=model, api_key=self.api_key)

    @property
    def image_to_text_format(self):
        """
        Default prompt format for generating vibrant and dynamic video descriptions.
        
        Returns:
            str: The default prompt string.
        """
        return """I want to generate a vibrant and dynamic video using the following image and a Large Vision Model. The video should be visually engaging and rich in detail. Create a prompt for the video based on following requirements. High Detail & Realism: Preserve intricate textures and visual elements from the image. Energy & Vibrancy: Use dynamic movement, rich colors, and smooth transitions. Cinematic Quality: Apply effects like depth of field, natural lighting, and camera movements. Smooth Scene Progression: Ensure logical and fluid storytelling without abrupt changes. Natural Motion & Interaction: Any movements should feel organic and visually coherent. High-Quality Rendering: Avoid jitter, maintain consistency, and output in high resolution. Please generate a visually compelling video based on these guidelines. Do not itemize the prompt. Write in single paragraph. Do not use special charecters."""

    def generate_text(self, image_url: str, prompt: str = None) -> str:
        """
        Generate text based on an image URL and a prompt.
        
        Args:
            image_url (str): URL of the image to process.
            prompt (str, optional): The text prompt to guide the generation. 
                                   Defaults to image_to_text_format if None.
        
        Returns:
            str: The generated text response from the model.
        """
        # Use the default prompt if none provided
        if prompt is None:
            prompt = self.image_to_text_format

        message = HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": image_url}}
            ]
        )
        try:
            response = self.model.invoke([message])
            return response.content
        except Exception as e:
            raise Exception(f"Error generating text from image URL: {e}")

    def generate_bash_cmd(self, image_url: str, text_prompt: str = None) -> str:
        """
        Generate a one-line bash command to process the image and generate videos, 
        with unique_id generated in bash.
        
        Args:
            image_url (str): URL of the image to download and process.
            text_prompt (str, optional): The prompt to generate text for the video.
                                        Defaults to image_to_text_format if None.
        
        Returns:
            str: A one-line bash command.
        """
        # Generate the text prompt using the generate_text method
        generated_prompt = self.generate_text(image_url, text_prompt)
        
        # Escape quotes in the generated prompt for bash compatibility
        escaped_prompt = generated_prompt.replace('"', '\\"')
        
        # Construct the bash command with unique_id generated via uuidgen
        cmd = (
            f"unique_id=$(uuidgen) && mkdir -p i2v_${{unique_id}} && "
            f"curl -o i2v_${{unique_id}}/image.jpg {image_url} && "
            f"for i in {{1..10}}; do torchrun --nproc_per_node=4 generate.py "
            f"--task i2v-14B --size \"832*480\" --ckpt_dir ./Wan2.1-I2V-14B-480P "
            f"--image i2v_${{unique_id}}/image.jpg --dit_fsdp --t5_fsdp --ulysses_size 4 "
            f"--save_file kidcat/${{i}}.mp4 --prompt \"{escaped_prompt}\"; done"
        )
        
        return cmd

# Example usage
if __name__ == "__main__":
    try:
        converter = ImageToTextWan(model="gpt-4o-mini")
        image_url = "https://example.com/images/man.jpg"
        
        # Using default prompt
        bash_cmd_default = converter.generate_bash_cmd(image_url)
        print("Generated Bash Command (Default Prompt):")
        print(bash_cmd_default)
        
        # Using custom prompt
        custom_prompt = "Describe the scene in a simple way."
        bash_cmd_custom = converter.generate_bash_cmd(image_url, custom_prompt)
        print("\nGenerated Bash Command (Custom Prompt):")
        print(bash_cmd_custom)
        
    except Exception as e:
        print(f"Error: {e}")