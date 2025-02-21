import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram import InputMediaPhoto
import aiohttp
import os

from zoza.image_to_text import ImageToText
from zoza.text_to_image import TextToImage

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
dotenv_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=dotenv_path)
TOKEN = os.getenv("BOT_TOKEN")

# Initialize AI models
i2t_model = "qwen/qwen-vl-plus:free"
# i2t_model = "google/gemini-2.0-flash-thinking-exp:free"
image_to_text_model = ImageToText(i2t_model)  # Example model
text_to_image_model = TextToImage.from_meta()

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("📸 Send me an image or text, and I'll generate an image for you!")

# Handle photo input
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    photo = update.message.photo[-1]  # Get the highest resolution photo
    file = await photo.get_file()
    
    image_url = file.file_path  # Get the direct Telegram file URL
    logger.info("Image received: %s", image_url)

    image_to_text_format = """
    "Describe the image based on following format."
    'Image Description: Put long description of the image in here'
    'Object: Put the name of dominant object in image here'
    'Color scheme: Put color scheme of image here'
    'Background: Put short description of the image background here'
    """

    image_to_text_format = """
    "Describe the image in detail using the following format. Strictly follow the template and do not include labels like 'Image Description:', 'Object:', 'Color scheme:', or 'Background:' in your response. Only provide the content for each section as described below."
    'Put a long and detailed description of the image here, covering all visible elements, actions, and context.'
    'Put the name of the dominant object(s) in the image here, along with their appearance, position, and notable features.'
    'Put the overall color scheme of the image here, including dominant colors, contrasts, and any notable color patterns or tones.'
    'Put a detailed description of the background here, including its setting, elements, and how it relates to the main objects.'
    """

    # Run image-to-text
    extracted_text = image_to_text_model.analyze_image(image_url, text=image_to_text_format)
    
    if not extracted_text:
        await update.message.reply_text("❌ Sorry, I couldn't extract text from this image. Try another one!")
        return
    
    await process_text(update, extracted_text)

# Handle text input
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    await process_text(update, text)



import aiohttp
import os
import subprocess
from telegram import InputMediaPhoto, InputMediaVideo

async def download_video(video_url: str, filename: str) -> str:
    """Downloads a video from a URL and saves it locally."""
    async with aiohttp.ClientSession() as session:
        async with session.get(video_url) as resp:
            if resp.status == 200:
                filepath = f"/tmp/{filename}"  
                with open(filepath, "wb") as f:
                    f.write(await resp.read())
                return filepath
    return None

async def merge_videos(video_paths: list, output_path: str) -> bool:
    """Merges multiple videos into one using ffmpeg."""
    if len(video_paths) < 2:
        return False  # No need to merge if there's only one video

    list_file = "/tmp/video_list.txt"
    with open(list_file, "w") as f:
        for video in video_paths:
            f.write(f"file '{video}'\n")

    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", list_file, "-c", "copy", output_path
    ]
    
    process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return process.returncode == 0

async def process_text(update: Update, text: str) -> None:
    await update.message.reply_text(f"📝 Using text: {text}\nGenerating media...")

    result = text_to_image_model(prompt=text)
    logger.info("text to image result: %s", result)

    if not result or not isinstance(result, tuple) or len(result) != 2:
        await update.message.reply_text("❌ Failed to generate any media. Try again.")
        return
    
    image_urls, video_urls = result
    media_sent = False
    video_paths = []

    # Handle Images
    if image_urls:
        await update.message.reply_text("Sending generated images...")
        media_group = [InputMediaPhoto(media=url) for url in image_urls[:4]]
        try:
            await update.message.reply_media_group(media=media_group)
            media_sent = True
        except Exception as e:
            logger.error(f"Failed to send images: {str(e)}")
            await update.message.reply_text(f"❌ Error sending images: {str(e)}")

    # Handle Videos
    if video_urls:
        await update.message.reply_text("Downloading videos...")
        for idx, video_url in enumerate(video_urls[:4]):  # Limit to 4 videos
            video_path = await download_video(video_url, f"video_{idx}.mp4")
            if video_path:
                video_paths.append(video_path)

        if video_paths:
            await update.message.reply_text("Sending videos as a group...")
            media_group = []
            for video_path in video_paths:
                try:
                    with open(video_path, "rb") as video_file:
                        media_group.append(InputMediaVideo(media=video_file))
                except Exception as e:
                    logger.error(f"Failed to prepare video: {str(e)}")

            # Send grouped videos
            if media_group:
                try:
                    await update.message.reply_media_group(media=media_group)
                    media_sent = True
                except Exception as e:
                    logger.error(f"Failed to send video group: {str(e)}")
                    await update.message.reply_text(f"❌ Error sending video group: {str(e)}")

        # Merge videos
        if len(video_paths) > 1:
            await update.message.reply_text("Merging videos...")
            merged_video_path = "/tmp/merged_video.mp4"
            if await merge_videos(video_paths, merged_video_path):
                try:
                    with open(merged_video_path, "rb") as merged_video:
                        await update.message.reply_video(merged_video)
                    os.remove(merged_video_path)  # Cleanup
                except Exception as e:
                    logger.error(f"Failed to send merged video: {str(e)}")
                    await update.message.reply_text(f"❌ Error sending merged video: {str(e)}")

        # Cleanup individual videos
        for video_path in video_paths:
            os.remove(video_path)

    if not media_sent:
        await update.message.reply_text("❌ No media was successfully sent.")




# Set up bot
def main() -> None:
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    application.run_polling()

if __name__ == "__main__":
    main()
