import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
    ContextTypes
)
import aiohttp
import subprocess

from zoza.image_to_text import ImageToText
from zoza.text_to_image import TextToImage

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up file handler for image URLs
os.makedirs("./data", exist_ok=True)  # Create data directory if it doesn't exist
image_url_logger = logging.getLogger('image_url_logger')
image_url_logger.setLevel(logging.INFO)
fh = logging.FileHandler('./data/image_url.log')
fh.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(message)s')
fh.setFormatter(formatter)
image_url_logger.addHandler(fh)

# Load environment variables
dotenv_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=dotenv_path)
TOKEN = os.getenv("BOT_TOKEN")

# Initialize AI models
i2t_model = "qwen/qwen-vl-plus:free"
image_to_text_model = ImageToText(i2t_model)
text_to_image_model = TextToImage.from_meta()

# Define path_to_sound (you might want to adjust this)
path_to_sound = "./data/16.mp3"  # Add your audio file path here

# States for ConversationHandler
INPUT, STYLE_SELECTION, CUSTOM_STYLE = range(3)

# Download video from URL
async def download_video(video_url: str, filename: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(video_url) as resp:
            if resp.status == 200:
                filepath = f"/tmp/{filename}"  
                with open(filepath, "wb") as f:
                    f.write(await resp.read())
                return filepath
    return None

# Merge multiple videos
async def merge_videos(video_paths: list, output_path: str) -> bool:
    if len(video_paths) < 2:
        return False  

    list_file = "/tmp/video_list.txt"
    with open(list_file, "w") as f:
        for video in video_paths:
            f.write(f"file '{video}'\n")

    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_file, "-c", "copy", output_path]
    process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return process.returncode == 0

# Add audio to video
async def add_audio_to_video(video_path: str, output_path: str, audio_path: str) -> bool:
    cmd_get_duration = ["ffprobe", "-i", video_path, "-show_entries", "format=duration", "-v", "quiet", "-of", "csv=p=0"]
    process = subprocess.run(cmd_get_duration, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    video_duration = float(process.stdout.decode().strip()) if process.returncode == 0 else None

    if not video_duration:
        return False

    cmd = [
        "ffmpeg", "-y", "-i", video_path, "-i", audio_path,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-t", str(video_duration), "-map", "0:v:0", "-map", "1:a:0",
        "-shortest", output_path
    ]
    process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return process.returncode == 0

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Hello! Please send me an image or text to process.")
    return INPUT

async def handle_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.photo:
        photo_file = await update.message.photo[-1].get_file()
        image_url = photo_file.file_path
        # Log the image URL
        image_url_logger.info(image_url)
        extracted_text = image_to_text_model.analyze_image(image_url, text="Generate image")
        await update.message.reply_text(f"Extracted text: {extracted_text}")
    else:
        extracted_text = update.message.text
        await update.message.reply_text(f"Received text: {extracted_text}")

    context.user_data['extracted_text'] = extracted_text

    keyboard = [
        [InlineKeyboardButton("Default", callback_data="Default")],
        [InlineKeyboardButton("Iranian", callback_data="Iranian")],
        [InlineKeyboardButton("Old fashion", callback_data="Old fashion")],
        [InlineKeyboardButton("Technological", callback_data="Technological")],
        [InlineKeyboardButton("Custom style", callback_data="Custom style")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Please select a style:", reply_markup=reply_markup)
    return STYLE_SELECTION

async def style_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    style = query.data
    extracted_text = context.user_data['extracted_text']

    if style == "Custom style":
        await query.edit_message_text("Please enter your custom style name:")
        return CUSTOM_STYLE
    
    if style == "Default":
        final_text = extracted_text
    elif style == "Iranian":
        final_text = f"{extracted_text} Style is Iranian"
    elif style == "Old fashion":
        final_text = f"{extracted_text} Style is Old fashion"
    elif style == "Technological":
        final_text = f"{extracted_text} Style is Technological"

    await query.edit_message_text(f"Prompt: {final_text}")  # Moved here to show prompt before processing
    result = text_to_image_model(prompt=final_text)

    # Video processing addition
    if not result or not isinstance(result, tuple) or len(result) != 2:
        await query.edit_message_text("❌ Failed to generate any media. Try again.")
        return ConversationHandler.END

    image_urls, video_urls = result
    video_paths = []

    if video_urls:
        await query.edit_message_text("Downloading videos...")
        for idx, video_url in enumerate(video_urls[:4]):  # Limiting to 4 videos
            video_path = await download_video(video_url, f"video_{idx}.mp4")
            if video_path:
                video_paths.append(video_path)

        if len(video_paths) > 1:
            merged_video_path = "/tmp/merged_video.mp4"
            merged_with_audio_path = "/tmp/merged_with_audio.mp4"

            if await merge_videos(video_paths, merged_video_path):
                if await add_audio_to_video(merged_video_path, merged_with_audio_path, path_to_sound):
                    with open(merged_with_audio_path, "rb") as merged_video:
                        await query.message.reply_video(merged_video)
                    os.remove(merged_with_audio_path)
                os.remove(merged_video_path)

        for video_path in video_paths:
            os.remove(video_path)

    return ConversationHandler.END

async def custom_style(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    custom_style = update.message.text
    extracted_text = context.user_data['extracted_text']
    
    final_text = f"{extracted_text} Style is {custom_style}"
    await update.message.reply_text(f"Prompt: {final_text}")
    result = text_to_image_model(prompt=final_text)

    # Video processing addition
    if not result or not isinstance(result, tuple) or len(result) != 2:
        await update.message.reply_text("❌ Failed to generate any media. Try again.")
        return ConversationHandler.END

    image_urls, video_urls = result
    video_paths = []

    if video_urls:
        await update.message.reply_text("Downloading videos...")
        for idx, video_url in enumerate(video_urls[:4]):
            video_path = await download_video(video_url, f"video_{idx}.mp4")
            if video_path:
                video_paths.append(video_path)

        if len(video_paths) > 1:
            merged_video_path = "/tmp/merged_video.mp4"
            merged_with_audio_path = "/tmp/merged_with_audio.mp4"

            if await merge_videos(video_paths, merged_video_path):
                if await add_audio_to_video(merged_video_path, merged_with_audio_path, path_to_sound):
                    with open(merged_with_audio_path, "rb") as merged_video:
                        await update.message.reply_video(merged_video)
                    os.remove(merged_with_audio_path)
                os.remove(merged_video_path)

        for video_path in video_paths:
            os.remove(video_path)

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "Available commands:\n"
        "/start - Start generating images\n"
        "/help - Show this help message\n"
        "/cancel - Cancel current operation"
    )
    await update.message.reply_text(help_text)

async def set_bot_commands(application: Application) -> None:
    commands = [
        BotCommand("start", "Start generating images"),
        BotCommand("help", "Show help information"),
        BotCommand("cancel", "Cancel current operation")
    ]
    await application.bot.set_my_commands(commands)

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            INPUT: [MessageHandler(filters.PHOTO | filters.TEXT & ~filters.COMMAND, handle_input)],
            STYLE_SELECTION: [CallbackQueryHandler(style_selection)],
            CUSTOM_STYLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, custom_style)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", help_command))
    application.post_init = set_bot_commands
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()