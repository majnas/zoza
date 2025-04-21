from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
import os
import requests

from image_to_text_openrouter import ImageToTextOpenRouter
from image_to_text_ollama import ImageToTextOllama
from image_to_text_openai import ImageToTextOpenAI
from wan_cmd_generator import WanCmdGenerator
import utils

app = FastAPI(title="Image-to-Text API")

SERVICE_NAME = os.getenv("SERVICE_NAME")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SERVER_LISTEN_IP = os.getenv("SERVER_LISTEN_IP")
SERVER_LISTEN_PORT = os.getenv("SERVER_LISTEN_PORT")

# Define request model
class ImageRequest(BaseModel):
    image_url: str
    engine: str = "OpenAI"

class ImageRequestList(BaseModel):
    image_url_list: list
    engine: str = "OpenAI"


# Initialize ImageToText model
OPENROUTER_MODEL_NAME = "qwen/qwen-vl-plus:free"
OPENAI_MODEL_NAME="gpt-4o-mini"
OLLAMA_MODEL_NAME = "granite3.2-vision:2b"

image_to_text_openrouter = ImageToTextOpenRouter(model=OPENROUTER_MODEL_NAME, api_key=OPENROUTER_API_KEY)
image_to_text_ollama = ImageToTextOllama(model=OLLAMA_MODEL_NAME)
image_to_text_openai = ImageToTextOpenAI(model=OPENAI_MODEL_NAME, api_key=OPENAI_API_KEY)

# Existing endpoint
@app.post(f"/{SERVICE_NAME}/invoke")
def invoke(request: ImageRequest) -> Dict[str, str]:
    try:
        if request.engine == "OpenAI":
            action_list = ["The person in image is smiling and while looking at camera winking."]
            result = image_to_text_openai.analyze_image(request.image_url, action_list)
        elif request.engine == "OpenRouter":
            result = image_to_text_openrouter.analyze_image(request.image_url)
        elif request.engine == "Ollama":
            image_path = utils.download_image_by_url(image_url=request.image_url)
            result = image_to_text_ollama.analyze_image(image_path=str(image_path))
            os.remove(image_path)
        return {"description": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# New endpoint for ImageToTextWan
@app.post(f"/{SERVICE_NAME}/generate_wan_cmd")
def generate_wan_cmd(request: ImageRequestList) -> Dict[str, str]:
    """
    Endpoint to generate a Bash command by analyzing an image from a URL using ImageToTextOllama.
    
    :param request: ImageRequest object containing the image URL.
    :return: Dictionary with the generated Bash command or description.
    :raises HTTPException: If an error occurs during processing.
    """
    try:
        image_url_list = []
        text_prompt_list = []
        for image_url in request.image_url_list:
            req = ImageRequest(image_url=image_url)
            response = invoke(request=req)
            image_url_list.append(image_url)
            text_prompt_list.append(response.get("description"))        

        bash_cmd_default = WanCmdGenerator.generate_bash_cmd(image_url_list=image_url_list, text_prompt_list=text_prompt_list)
        return {"bash_command": bash_cmd_default}

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to download image: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")