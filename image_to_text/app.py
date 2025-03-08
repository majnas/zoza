from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
import os
from image_to_text import ImageToText
from image_to_text_wan import ImageToTextWan

app = FastAPI(title="Image-to-Text API")

SERVICE_NAME = os.getenv("SERVICE_NAME")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SERVER_LISTEN_IP = os.getenv("SERVER_LISTEN_IP")
SERVER_LISTEN_PORT = os.getenv("SERVER_LISTEN_PORT")

# Define request model
class ImageRequest(BaseModel):
    image_url: str

# Initialize ImageToText model
MODEL_NAME = "qwen/qwen-vl-plus:free"
WAN_MODEL_NAME="gpt-4o-mini"

if not OPENROUTER_API_KEY:
    raise ValueError("API key is not set. Please set the OPENROUTER_API_KEY environment variable.")

image_to_text = ImageToText(model=MODEL_NAME, api_key=OPENROUTER_API_KEY)
image_to_text_wan = ImageToTextWan(model=WAN_MODEL_NAME, api_key=OPENAI_API_KEY)

# Existing endpoint
@app.post(f"/{SERVICE_NAME}/invoke")
def invoke(request: ImageRequest) -> Dict[str, str]:
    try:
        result = image_to_text.analyze_image(request.image_url)
        return {"description": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# New endpoint for ImageToTextWan
@app.post(f"/{SERVICE_NAME}/generate-bash")
def generate_bash(request: ImageRequest) -> Dict[str, str]:
    try:
        bash_cmd_default = image_to_text_wan.generate_bash_cmd(request.image_url)
        return {"bash_command": bash_cmd_default}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
