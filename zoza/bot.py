import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

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
image_to_text_model = ImageToText("qwen/qwen-vl-plus:free")  # Example model
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

# Process text (either extracted from an image or directly from user input)
async def process_text(update: Update, text: str) -> None:
    await update.message.reply_text(f"📝 Using text: {text}\nGenerating media...")

    # Run text-to-image
    result = text_to_image_model(prompt=text)
    logger.info("text to image result: %s", result)

    # Check if result is valid and contains URLs
    if not result or not isinstance(result, tuple) or len(result) != 2:
        await update.message.reply_text("❌ Failed to generate any media. Try again.")
        return
    
    image_urls, video_urls = result

    # Track if any media was successfully sent
    media_sent = False

    # Handle images
    if image_urls:
        await update.message.reply_text("Sending generated images...")
        for image_url in image_urls:
            try:
                await update.message.reply_photo(photo=image_url)
                media_sent = True
            except Exception as e:
                logger.error(f"Failed to send image {image_url}: {str(e)}")
                await update.message.reply_text(f"❌ Error sending an image: {str(e)}")
    else:
        await update.message.reply_text("⚠️ No images were generated.")

    # Handle videos
    if video_urls:
        await update.message.reply_text("Sending generated videos...")
        for video_url in video_urls:
            try:
                await update.message.reply_video(video=video_url)
                media_sent = True
            except Exception as e:
                logger.error(f"Failed to send video {video_url}: {str(e)}")
                await update.message.reply_text(f"❌ Error sending a video: {str(e)}")
    else:
        await update.message.reply_text("⚠️ No videos were generated.")

    # If no media was sent successfully
    if not media_sent and not image_urls and not video_urls:
        await update.message.reply_text("❌ No media was generated from the text.")

# Set up bot
def main() -> None:
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    application.run_polling()

if __name__ == "__main__":
    main()
