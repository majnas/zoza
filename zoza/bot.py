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
    await update.message.reply_text(f"📝 Using text: {text}\nGenerating an image...")

    # Run text-to-image
    result = text_to_image_model(prompt=f"Imagine: Generate an image with following dscription. {text}")
    logger.info("text to image result: %s", result)

    if not result or "media" not in result or not result.get("media"):
        await update.message.reply_text("❌ Failed to generate an image. Try again.")
        return

    # Send the generated image
    for media in result["media"]:
        image_url = media["url"]
        await update.message.reply_photo(photo=image_url)

# Set up bot
def main() -> None:
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    application.run_polling()

if __name__ == "__main__":
    main()
