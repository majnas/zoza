import os
import sys
import logging
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
import hupper

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up file handler for image URLs
os.makedirs("./data", exist_ok=True)  # Create data directory if it doesn't exist
logger = logging.getLogger('logger')
logger.setLevel(logging.INFO)
fh = logging.FileHandler('./data/image_url.log')
fh.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

# Load environment variables
TOKEN = os.getenv("BOT_TOKEN")

# Define path_to_sound (you might want to adjust this)
path_to_sound = "./asset/music/16.mp3"  # Add your audio file path here

# Define API endpoints using the docker service names and internal ports
IMAGE_TO_TEXT_URL = "http://image_to_text:8000/IMAGE_TO_TEXT/invoke"
TEXT_TO_IMAGE_URL = "http://text_to_image:8000/TEXT_TO_IMAGE/invoke/"
IMAGE_TO_TEXT_WAN_URL = "http://image_to_text:8000/IMAGE_TO_TEXT/generate-bash"

# States for ConversationHandler
INPUT, STYLE_SELECTION, CUSTOM_STYLE, WANCMD_WAITING = range(4)

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
        logger.info(image_url)
        async with aiohttp.ClientSession() as session:
            async with session.post(
                IMAGE_TO_TEXT_URL,
                json={"image_url": image_url},
                headers={"accept": "application/json", "Content-Type": "application/json"}
            ) as resp:
                data = await resp.json()
                extracted_text = data.get("description", )
                logger.info("extracted_text: %s", extracted_text)

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

    await query.edit_message_text(f"Prompt: {final_text} \n⏳ Generate media ...")

    async with aiohttp.ClientSession() as session:
        async with session.post(
            TEXT_TO_IMAGE_URL,
            json={"prompt": final_text},
            headers={"accept": "application/json", "Content-Type": "application/json"}
        ) as resp:
            result = await resp.json()

    if not result or "image_urls" not in result or "video_urls" not in result:
        await query.edit_message_text("❌ Failed to generate any media. Try again.")
        return ConversationHandler.END  

    image_urls = result.get("image_urls")
    video_urls = result.get("video_urls")
    logger.info(image_urls)
    logger.info(video_urls)

    if not image_urls or not video_urls:
        await query.edit_message_text("❌ There is no image and video generated!")
        return ConversationHandler.END

    video_paths = []

    if video_urls:
        await query.edit_message_text("⏳ Downloading videos...")
        for idx, video_url in enumerate(video_urls[:4]):  # Limiting to 4 videos
            video_path = await download_video(video_url, f"video_{idx}.mp4")
            if video_path:
                video_paths.append(video_path)

        if len(video_paths) > 1:
            merged_video_path = "/tmp/merged_video.mp4"
            merged_with_audio_path = "/tmp/merged_with_audio.mp4"

            await query.edit_message_text("⏳ Merge videos...")
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
    await update.message.reply_text(f"Prompt: {final_text} \n⏳ Generate media ...")

    async with aiohttp.ClientSession() as session:
        async with session.post(
            TEXT_TO_IMAGE_URL,
            json={"prompt": final_text},
            headers={"accept": "application/json", "Content-Type": "application/json"}
        ) as resp:
            result = await resp.json()

    if not result or "image_urls" not in result or "video_urls" not in result:
        await update.message.reply_text("❌ Failed to generate any media. Try again.")
        return ConversationHandler.END

    image_urls = result.get("image_urls")
    video_urls = result.get("video_urls")

    if not image_urls or not video_urls:
        await update.message.reply_text("❌ There is no image and video generated!")
        return ConversationHandler.END

    video_paths = []

    if video_urls:
        await update.message.reply_text("⏳ Downloading videos...")
        for idx, video_url in enumerate(video_urls[:4]):
            video_path = await download_video(video_url, f"video_{idx}.mp4")
            if video_path:
                video_paths.append(video_path)

        if len(video_paths) > 1:
            await update.message.reply_text("⏳ Merge videos...")
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

async def wancmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info("Starting /wancmd command processing")
    await update.message.reply_text("Please send an image to process with /wancmd")
    context.user_data['waiting_for_wancmd_image'] = True
    return WANCMD_WAITING

async def wancmd_process_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:    
    if not context.user_data.get('waiting_for_wancmd_image', False):
        logger.info("Not in WANCMD_WAITING state, ignoring message")
        return ConversationHandler.END

    if update.message.photo:
        photo_file = await update.message.photo[-1].get_file()
        image_url = photo_file.file_path
        logger.info(f"Received image URL: {image_url}")
        
        await update.message.reply_text("⏳ Processing image with /wancmd...")
        
        try:
            async with aiohttp.ClientSession() as session:
                logger.info(f"Sending POST request to {IMAGE_TO_TEXT_WAN_URL}")
                
                async with session.post(
                    IMAGE_TO_TEXT_WAN_URL,
                    json={"image_url": image_url},
                    headers={"accept": "application/json", "Content-Type": "application/json"}
                ) as resp:
                    logger.info(f"Response status: {resp.status}")
                    
                    if resp.status == 200:
                        data = await resp.json()
                        # Changed from "description" to "bash_command"
                        response_text = data.get("bash_command", "No bash command available")
                        logger.info(f"Extracted response_text: \n{response_text}")
                        await update.message.reply_text(f"{response_text}")
                    else:
                        logger.error(f"API request failed with status {resp.status}")
                        await update.message.reply_text(f"❌ Failed to process image (HTTP {resp.status})")
        except Exception as e:
            logger.error(f"Error in wancmd_process_image: {str(e)}", exc_info=True)
            await update.message.reply_text(f"❌ Error processing image: {str(e)}")
    else:
        logger.info("No photo in message")
        await update.message.reply_text("Please send an image to process with /wancmd")

    # Reset the state
    context.user_data['waiting_for_wancmd_image'] = False
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Operation cancelled.")
    context.user_data['waiting_for_wancmd_image'] = False
    return ConversationHandler.END

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "Available commands:\n"
        "/start - Start generating images\n"
        "/help - Show this help message\n"
        "/cancel - Cancel current operation\n"
        "/wancmd - Generate bash response from image"
    )
    await update.message.reply_text(help_text)

async def set_bot_commands(application: Application) -> None:
    commands = [
        BotCommand("start", "Start generating images"),
        BotCommand("help", "Show help information"),
        BotCommand("cancel", "Cancel current operation"),
        BotCommand("wancmd", "Generate bash response from image")
    ]
    await application.bot.set_my_commands(commands)

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("wancmd", wancmd_start)
        ],
        states={
            INPUT: [MessageHandler(filters.PHOTO | filters.TEXT & ~filters.COMMAND, handle_input)],
            STYLE_SELECTION: [CallbackQueryHandler(style_selection)],
            CUSTOM_STYLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, custom_style)],
            WANCMD_WAITING: [MessageHandler(filters.PHOTO | filters.TEXT & ~filters.COMMAND, wancmd_process_image)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", help_command))
    application.post_init = set_bot_commands
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    # Start the hupper reloader
    reloader = hupper.start_reloader('bot.main')    
    main()