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
# image_to_text_model = ImageToText(i2t_model)  # Example model
# text_to_image_model = TextToImage.from_meta()

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
    extracted_text = "Sample text"
    # extracted_text = image_to_text_model.analyze_image(image_url, text=image_to_text_format)
    
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

path_to_sound = "./data/16.mp3"  # Path to background audio file

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

async def add_audio_to_video(video_path: str, output_path: str, audio_path: str) -> bool:
    """Adds background music to the merged video, trimming the audio if necessary."""
    cmd_get_duration = [
        "ffprobe", "-i", video_path, "-show_entries", "format=duration",
        "-v", "quiet", "-of", "csv=p=0"
    ]
    
    process = subprocess.run(cmd_get_duration, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    video_duration = float(process.stdout.decode().strip()) if process.returncode == 0 else None

    if not video_duration:
        return False

    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", audio_path,
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-t", str(video_duration),  # Trim audio to match video length
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-shortest",
        output_path
    ]

    process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return process.returncode == 0

async def process_text(update: Update, text: str) -> None:
    await update.message.reply_text(f"📝 Using text: {text}\nGenerating media...")

    # result = text_to_image_model(prompt=text)
    result = (['https://scontent.fmel3-1.fna.fbcdn.net/o1/v/t0/f2/m340/AQNxsetgFipEi6FbRbgZxpALAdRKWI0BRahdJ2cJsnoC_grVCgX-eYawtOZVFp_lvTSSsYwkYHMSwOxxlO2iNbLmHDH-JftIPS-1iPwxui87u3SxoxrT03wa8AbfOduEbc1D74HPlVEHDX4eAYmswvpk5vw1.jpeg?_nc_ht=scontent.fmel3-1.fna.fbcdn.net&_nc_cat=106&ccb=9-4&oh=00_AYB-iHPP0ltuUocjCw_1Hay6piBRd2X4Zd40AbbVC-RQXw&oe=67BB23A9&_nc_sid=5b3566', 'https://scontent.fmel3-1.fna.fbcdn.net/o1/v/t0/f2/m340/AQMQ6JeQa81c9ZUK6rzSriDt7DgdBEPIl0MfDumZ3QoO3AdMFeAGpp4c4Cw4mO35SO_5NghwYKkvd94PPm2re2g_Lh8lGMcbJKtRYYwxtNx489h_vahzpWB46CM1JbJt3IPmqAVdj_NHi4kZmyEhmBMv7N4JOA.jpeg?_nc_ht=scontent.fmel3-1.fna.fbcdn.net&_nc_cat=110&ccb=9-4&oh=00_AYAmK4xEjUUFyPMHw5OUDk9SoAu8Y6fAalhF7vnjvgHM3w&oe=67BB2755&_nc_sid=5b3566', 'https://scontent.fmel3-1.fna.fbcdn.net/o1/v/t0/f2/m340/AQNUEOR0srKwYuYsEhBUOwRWxpxMORTcM40d6J50bR5cIwiGeNGHaHwlUBouRKmx7ObPvcl7F-ICqsWnX5GDo6hARl1Ajh-ntk1z60vlIuIhXGnwFY7zkiLHC_DOYwIaQ_PVb5_24wKAG3KWMgctF3QcyQI1hQ.jpeg?_nc_ht=scontent.fmel3-1.fna.fbcdn.net&_nc_cat=102&ccb=9-4&oh=00_AYA7qMnRXWdgr4ttbQksTnryycjv5zejUoFhx4TypW5ihQ&oe=67BB4585&_nc_sid=5b3566', 'https://scontent.fmel3-1.fna.fbcdn.net/o1/v/t0/f2/m340/AQPpyq6UmW9pILSQdPqulH2L8QHk2eTw3DGKwzBXcTod-iIhNwD6YiawGe_unV-CsuPEkIUf5Y9kcjgRPS3wh8jKZWrUKTQblpop4v7UKHMf6CGvkbtujcmStr9ZoEI-iuOu0go3d0fcKf697fwOTT9dHusZcw.jpeg?_nc_ht=scontent.fmel3-1.fna.fbcdn.net&_nc_cat=110&ccb=9-4&oh=00_AYCLeLB-czxcens_K_g3MLHPJtOkiuw2IMXDU4OgXcvVhw&oe=67BB4195&_nc_sid=5b3566'], ['https://scontent.fmel3-1.fna.fbcdn.net/o1/v/t0/f2/m257/AQPNDuVHFK9bbH1dHjaYrd04WtgtR1kG2xV6eQkfBlfqLhhoHjStTDeJnKsXTIvVCG2_DEHwlDkJHDrCtpZTfpUYUk_jqjS0B96ABxvSUo1UoTgysW4R7grfwQcF9g.mp4?_nc_ht=scontent.fmel3-1.fna.fbcdn.net&_nc_cat=110&ccb=9-4&oh=00_AYAgWVIMaQW6jqPTJa4dzRV5iJYMUb0rbrn6bzf_k7kI-g&oe=67BB18E4&_nc_sid=5b3566', 'https://scontent.fmel3-1.fna.fbcdn.net/o1/v/t0/f2/m248/AQMZ4eOgxE46kno_RvyhR5w2eE7Fqomgt8jtz6wu8x1bfRlZm_48PMXeLr8ieCabptrnTFFU72rHK1AUN9AHROXXwquhz7CiqE9Mnr5Eca8nvaSj43rTO12ZSHLPYA.mp4?_nc_ht=scontent.fmel3-1.fna.fbcdn.net&_nc_cat=102&ccb=9-4&oh=00_AYAklfoaMe-E46MR4Ac8yzjqelL_IoIMjvGDd_iCkA9Z4Q&oe=67BB3638&_nc_sid=5b3566', 'https://scontent.fmel3-1.fna.fbcdn.net/o1/v/t0/f2/m338/AQPw1tqBqTy7TpD3DGTQLjIwF55SW_bnmFTLFcNlW5QWhJpKfBbCeRRBHZsVlXWUjom8sZlZxirAteCITCAQPct5Gk0402CEYAoTZkz5tUcFbgUQe9DX49e5DmIxQ9ee.mp4?_nc_ht=scontent.fmel3-1.fna.fbcdn.net&_nc_cat=103&ccb=9-4&oh=00_AYA0xsbhKKuFOGs5rQIXoLttrxagLpCRHyU_UvmLGKURKg&oe=67BB34EB&_nc_sid=5b3566', 'https://scontent.fmel3-1.fna.fbcdn.net/o1/v/t0/f2/m253/AQMaiKrcGF1Dhtl1Oe-qF1n6_VEK_S-cP5nWpe6wv7fYNn0vDrR4IsvFilj2SqIUtTl8SuDxwx3x8F5ztDgi8uq23zKbjmS9YC9y2z7_hZPZM1HvXQaQUkn5CMta4GGJ.mp4?_nc_ht=scontent.fmel3-1.fna.fbcdn.net&_nc_cat=111&ccb=9-4&oh=00_AYBJJ3jFqD7wEfrf2M85d7ACDPQpZ7wJm16AiUUyX8Z0Ew&oe=67BB1813&_nc_sid=5b3566'])
    logger.info("text to image result: %s", result)

    if not result or not isinstance(result, tuple) or len(result) != 2:
        await update.message.reply_text("❌ Failed to generate any media. Try again.")
        return
    
    image_urls, video_urls = result
    media_sent = False
    video_paths = []

    # Handle Images
    # if image_urls:
    #     await update.message.reply_text("Sending generated images...")
    #     media_group = [InputMediaPhoto(media=url) for url in image_urls[:4]]
    #     try:
    #         await update.message.reply_media_group(media=media_group)
    #         media_sent = True
    #     except Exception as e:
    #         logger.error(f"Failed to send images: {str(e)}")
    #         await update.message.reply_text(f"❌ Error sending images: {str(e)}")

    # Handle Videos
    if video_urls:
        await update.message.reply_text("Downloading videos...")
        for idx, video_url in enumerate(video_urls[:4]):  # Limit to 4 videos
            video_path = await download_video(video_url, f"video_{idx}.mp4")
            if video_path:
                video_paths.append(video_path)

        # if video_paths:
        #     await update.message.reply_text("Sending videos as a group...")
        #     media_group = []
        #     for video_path in video_paths:
        #         try:
        #             with open(video_path, "rb") as video_file:
        #                 media_group.append(InputMediaVideo(media=video_file))
        #         except Exception as e:
        #             logger.error(f"Failed to prepare video: {str(e)}")

        #     # Send grouped videos
        #     if media_group:
        #         try:
        #             await update.message.reply_media_group(media=media_group)
        #             media_sent = True
        #         except Exception as e:
        #             logger.error(f"Failed to send video group: {str(e)}")
        #             await update.message.reply_text(f"❌ Error sending video group: {str(e)}")

        # Merge videos and add sound
        if len(video_paths) > 1:
            await update.message.reply_text("Merging videos...")
            merged_video_path = "/tmp/merged_video.mp4"
            merged_with_audio_path = "/tmp/merged_with_audio.mp4"

            if await merge_videos(video_paths, merged_video_path):
                await update.message.reply_text("Adding background music...")

                if await add_audio_to_video(merged_video_path, merged_with_audio_path, path_to_sound):
                    try:
                        with open(merged_with_audio_path, "rb") as merged_video:
                            await update.message.reply_video(merged_video)
                        os.remove(merged_with_audio_path)  # Cleanup
                    except Exception as e:
                        logger.error(f"Failed to send merged video: {str(e)}")
                        await update.message.reply_text(f"❌ Error sending merged video: {str(e)}")

                os.remove(merged_video_path)  # Cleanup

        # Cleanup individual videos
        for video_path in video_paths:
            os.remove(video_path)

    # if not media_sent:
    #     await update.message.reply_text("❌ No media was successfully sent.")



# Set up bot
def main() -> None:
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    application.run_polling()

if __name__ == "__main__":
    main()
