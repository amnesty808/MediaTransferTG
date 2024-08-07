import os
import asyncio
import sys
from tqdm import tqdm
from pyrogram import Client
from pyrogram.errors import FloodWait, RPCError
from moviepy.editor import VideoFileClip
from pathlib import Path
import re
sys.path.append(str(Path(__file__).resolve().parent.parent))
import config

chat_id = int(os.environ.get('CHAT_ID'))
MAX_FILE_SIZE = int(os.environ.get('MAX_FILE_SIZE')) * 1024 * 1024


api_id = config.api_id                                
api_hash = config.api_hash    


allowed_media_types = ['mp4', 'gif', 'avi', 'mov', 'mkv', 'webm']
media_folder = os.path.join("..", "media")
os.makedirs(media_folder, exist_ok=True)

downloaded_media_file = "media.txt"

def create_thumbnail(video_path, thumbnail_path):
    clip = VideoFileClip(video_path)
    clip.save_frame(thumbnail_path, t=1)
    clip.close()

def load_downloaded_files():
    if os.path.exists(downloaded_media_file):
        with open(downloaded_media_file, "r", encoding="utf-8") as f:
            return set(f.read().splitlines())
    return set()

def save_downloaded_file(file_name):
    with open(downloaded_media_file, "a", encoding="utf-8") as f:
        f.write(file_name + "\n")

async def save_media(client, message):
    media = None
    file_name = None
    mime_type = None

    if message.video:
        mime_type = message.video.mime_type.split('/')[-1]
        if mime_type in allowed_media_types:
            media = message.video
            file_name = message.video.file_name
    elif message.document:
        mime_type = message.document.mime_type.split('/')[-1]
        if mime_type in allowed_media_types:
            media = message.document
            file_name = message.document.file_name

    if file_name is None:
        file_name = f"{message.id}.{mime_type}"

    # Проверка на русские символы
    if re.search(r'[а-яА-Я]', file_name):
        return

    unique_file_name = f"{chat_id}_{file_name}"

    if media is None or media.file_size > MAX_FILE_SIZE:
        return

    file_name_temp = os.path.join(media_folder, f"{unique_file_name}.temp")
    file_name_path = os.path.join(media_folder, unique_file_name)

    if unique_file_name not in downloaded_file_names:
        try:
            with tqdm(total=media.file_size, unit='B', unit_scale=True, desc=file_name_path, ncols=100) as pbar:
                def progress(current, total):
                    pbar.update(current - pbar.n)

                await client.download_media(message, file_name_temp, progress=progress)
            if os.path.exists(file_name_temp):
                os.rename(file_name_temp, file_name_path)
                if os.path.exists(file_name_path) and not file_name_path.endswith('.temp'):
                    downloaded_file_names.add(unique_file_name)
                    save_downloaded_file(unique_file_name)

        except Exception as e:
            print(f"Ошибка при скачивании {unique_file_name}: {e}")

async def download_media():
    global downloaded_file_names
    downloaded_file_names = load_downloaded_files()

    async with Client("my_account", api_id, api_hash) as app:
        offset_id = 0

        while True:
            try:
                messages = []
                async for message in app.get_chat_history(chat_id, offset_id=offset_id, limit=100):
                    messages.append(message)

                if not messages:
                    break

                for message in messages:
                    if message.media:
                        await save_media(app, message)
                    offset_id = message.id - 1

                await asyncio.sleep(5)

            except FloodWait as e:
                await asyncio.sleep(e.x)
            except RPCError as e:
                await asyncio.sleep(1)
            except Exception as e:
                await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(download_media())
