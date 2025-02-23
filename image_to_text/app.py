from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
import os
from image_to_text import ImageToText

app = FastAPI(title="image_to_text")

SERVICE_NAME = os.getenv("SERVICE_NAME")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
SERVER_LISTEN_IP = os.getenv("SERVER_LISTEN_IP")
SERVER_LISTEN_PORT = os.getenv("SERVER_LISTEN_PORT")

# Define request model
class ImageRequest(BaseModel):
    image_url: str

# Initialize ImageToText model
MODEL_NAME = "qwen/qwen-vl-plus:free"

if not OPENROUTER_API_KEY:
    raise ValueError("API key is not set. Please set the OPENROUTER_API_KEY environment variable.")

image_to_text = ImageToText(model=MODEL_NAME, api_key=OPENROUTER_API_KEY)

@app.post("/invoke")
def invoke(request: ImageRequest) -> Dict[str, str]:
    try:
        result = image_to_text.analyze_image(request.image_url)
        return {"description": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

