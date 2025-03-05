import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from text_to_image import TextToImage

SERVICE_NAME = os.getenv("SERVICE_NAME")
SERVER_LISTEN_IP = os.getenv("SERVER_LISTEN_IP")
SERVER_LISTEN_PORT = os.getenv("SERVER_LISTEN_PORT")

# Initialize FastAPI app
app = FastAPI(title="Text-to-Image API")

# Initialize TextToImage model
text_to_image = TextToImage.from_meta()
# text_to_image = TextToImage()

# Request model
class TextRequest(BaseModel):
    prompt: str

# Endpoint to generate image and video URLs
@app.post(f"/{SERVICE_NAME}/invoke/")
def generate_content(request: TextRequest):
    try:
        image_urls, video_urls = text_to_image(request.prompt)
        return {"image_urls": image_urls, "video_urls": video_urls}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
