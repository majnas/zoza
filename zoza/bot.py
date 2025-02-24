# bot.py
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
image_url_logger = logging.getLogger('image_url_logger')
image_url_logger.setLevel(logging.INFO)
fh = logging.FileHandler('./data/image_url.log')
fh.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(message)s')
fh.setFormatter(formatter)
image_url_logger.addHandler(fh)

# Load environment variables
TOKEN = os.getenv("BOT_TOKEN")

# Define path_to_sound (you might want to adjust this)
path_to_sound = "./asset/music/16.mp3"  # Add your audio file path here

# Define API endpoints using the docker service names and internal ports.
IMAGE_TO_TEXT_URL = "http://image_to_text:8000/IMAGE_TO_TEXT/invoke"
TEXT_TO_IMAGE_URL = "http://text_to_image:8000/TEXT_TO_IMAGE/invoke/"

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
        async with aiohttp.ClientSession() as session:
            async with session.post(
                IMAGE_TO_TEXT_URL,
                json={"image_url": image_url},
                headers={"accept": "application/json", "Content-Type": "application/json"}
            ) as resp:
                data = await resp.json()
                extracted_text = data.get("description", )
                image_url_logger.info("extracted_text: %s", extracted_text)

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

    await query.edit_message_text(f"Prompt: {final_text} \nGenerate media ...")

    # Call external TEXT_TO_IMAGE API using the Docker service name.
    async with aiohttp.ClientSession() as session:
        async with session.post(
            TEXT_TO_IMAGE_URL,
            json={"prompt": final_text},
            headers={"accept": "application/json", "Content-Type": "application/json"}
        ) as resp:
            result = await resp.json()

    # image_urls = ['https://scontent.fmel3-1.fna.fbcdn.net/o1/v/t0/f2/m340/AQNqTTRNPan-aCnMM4pSRXWavUTf7HIi8jwzuZN-WQnNEP1-gMSBqQFZUCKJOd5ZJZuJcu_dwyi4rXrroZVjEiIDaRFuHt9otKwdpGR-BszROCXSTSHaS_rT4iEptXbRy0BgDlU9qX1hHRRcxiB8nWABgy105Q.jpeg?_nc_ht=scontent.fmel3-1.fna.fbcdn.net&_nc_cat=110&ccb=9-4&oh=00_AYBn5Dvzuu1I1xt3aG9gmB7SUPJTP8oRyeeEw8xzIZqGBQ&oe=67BE50AD&_nc_sid=5b3566', 'https://scontent.fmel3-1.fna.fbcdn.net/o1/v/t0/f2/m340/AQMBuuJwW9RBZC_hTR-JcdliP77tXBFJdSlXj_bVT0G-LwYlp_9y0mFy7E3EteEWdSdnNaBJKCRtV9wTeKz30lpvECoZl-9jdaYhJF0o8qbS1SZbzT43zAz0a5SIE40IeuTkZg2AcfHp0I4yFBLTPEx2METJ.jpeg?_nc_ht=scontent.fmel3-1.fna.fbcdn.net&_nc_cat=104&ccb=9-4&oh=00_AYCboCCG2j26i8Mz2OcDAe-oJwViDcSUnIx_qtjb2uF_VQ&oe=67BE328B&_nc_sid=5b3566', 'https://scontent.fmel3-1.fna.fbcdn.net/o1/v/t0/f2/m340/AQPEXwL7rdoNdDf4buaC8yxqvS7QQViFtrx_lgeH-tCFjysniFUp-QySX_Bopstf5Cv3s14VxWR_B-L2f_jE2CMIULJcHg-9truMAMN0XGcALxyGpZO4hbqNOpIooZKVZvVit9TrRzxuvVybPI7lOciePzlUcg.jpeg?_nc_ht=scontent.fmel3-1.fna.fbcdn.net&_nc_cat=101&ccb=9-4&oh=00_AYBZoaRiBh2zvvIKhP5lhcYGF_UiB9xV9sQxbnz2wu3D6g&oe=67BE4144&_nc_sid=5b3566', 'https://scontent.fmel3-1.fna.fbcdn.net/o1/v/t0/f2/m340/AQP9G8arAZhiebTZWONMPXZ2yaIXnGw0P3sdV2HCKtyfFNqbu7MUii9G5pXaB80yF_lIlQ-KDnxu1czl2c5PUXd3Iq-E29Vd8m_4uus1w3g9xKIhpreBh9yon_16CMa3a25lk1jnFIsp5PSrfIUYLYraaK7EHA.jpeg?_nc_ht=scontent.fmel3-1.fna.fbcdn.net&_nc_cat=109&ccb=9-4&oh=00_AYC6B2WTWL0t1VdKw5jzgruFKgedFlG-h541tkFr9FdC9A&oe=67BE30F4&_nc_sid=5b3566']
    # video_urls = ['https://scontent.fmel3-1.fna.fbcdn.net/o1/v/t0/f2/m256/AQNagCN6NcaM_uJfbnBdNnJCf6Ap9vtBd5w5Yy1syK__yBa3adfMdADiv05kXvph9Eq8NSuqVz5d_N_sq6gvHufaBFC3534qoaT1QeFrbnK72EEM1eOyGq7RA26XMyLO.mp4?_nc_ht=scontent.fmel3-1.fna.fbcdn.net&_nc_cat=100&ccb=9-4&oh=00_AYAl3ORs5gOppPTLKAiaw7B73RHDCH0d2yhgSr25WJWcZA&oe=67BE1B1A&_nc_sid=5b3566', 'https://scontent.fmel3-1.fna.fbcdn.net/o1/v/t0/f2/m249/AQNcYRK3UbuH6zIgksdPac4Gdoj32zjsKYPcXTy50ciZ7Wok-DSMxpQGkyyGQsa_rnBecEbqyqosbgg96rInhBbK85yuQzwxHsoK9A15iFw1N-7-wGZ0xempfxivpTA9.mp4?_nc_ht=scontent.fmel3-1.fna.fbcdn.net&_nc_cat=103&ccb=9-4&oh=00_AYBNmwoxvKoRQp1au9IiCCuziEf3eQo17qTjZQjbE4vZYg&oe=67BE2123&_nc_sid=5b3566', 'https://scontent.fmel3-1.fna.fbcdn.net/o1/v/t0/f2/m251/AQMUlyhuZoM-c91t_BdnLF-nFDXMOxHjGzD4VyRMLtfdz2IRfoKLyXZIbCa_yjliCC_89NUoHcoEH2wuVnc9JhUC9o0pigDZ2lwLoTM3usJ5t7-5rlGop8wrr9Sb-yGL.mp4?_nc_ht=scontent.fmel3-1.fna.fbcdn.net&_nc_cat=109&ccb=9-4&oh=00_AYB7KbW4Ss99hiqnX9Cv1Ey5DOsNskx5Fy0RFIbX9nzlDg&oe=67BE2D59&_nc_sid=5b3566', 'https://scontent.fmel3-1.fna.fbcdn.net/o1/v/t0/f2/m338/AQMSN47XiN6CSeNG-lyhLYF1WPJjyly_42K_wF-FXuHJaZ7cM84UbVPEySZsq3ymQcj-jESQ_elLFIr6xUHDYfPs8F16qxcOyuqSZvDP64zLPviHL383rZDpCv6o72gt.mp4?_nc_ht=scontent.fmel3-1.fna.fbcdn.net&_nc_cat=111&ccb=9-4&oh=00_AYBr3toeaPy1ggiQo_QCsVxwSYR4WiP4LO6kida57V-ddg&oe=67BE3293&_nc_sid=5b3566']

    # result = {"image_urls": image_urls, "video_urls": video_urls}

    if not result or "image_urls" not in result or "video_urls" not in result:
        await query.edit_message_text("❌ Failed to generate any media. Try again.")
        return ConversationHandler.END  

    image_urls = result.get("image_urls")
    video_urls = result.get("video_urls")

    if not image_urls or not video_urls:
        await query.edit_message_text("❌ There is no image and video generated!")
        return ConversationHandler.END

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

            await query.edit_message_text("Merge videos...")
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
    await update.message.reply_text(f"Prompt: {final_text} \nGenerate media ...")

    # Call external TEXT_TO_IMAGE API using the Docker service name.
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
    # Start the hupper reloader
    reloader = hupper.start_reloader('bot.main')    
    main()
