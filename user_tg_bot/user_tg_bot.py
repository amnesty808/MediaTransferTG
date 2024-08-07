import asyncio
import os
import sys
from pathlib import Path
from pyrogram import Client
from pyrogram.types import InputMediaVideo, InputMediaPhoto
from moviepy.editor import VideoFileClip
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
import config

# Получаем значения переменных из окружения
mychat_id = os.environ.get('MYCHAT_ID')
chat_id = os.environ.get('CHAT_ID')
MAX_FILE_SIZE = int(os.environ.get('MAX_FILE_SIZE')) * 1024 * 1024


api_id = config.api_id                         
api_hash = config.api_hash                     



current_dir = Path(__file__).resolve().parent
media_folder = current_dir.parent / "media"
MAX_VIDEO_SIZE_MB = 30

print("Ждемс...")

async def send_media_group(app: Client, media_group: list, media_files: list):
    try:
        await app.send_media_group(mychat_id, media_group)
        for media in media_files:
            os.remove(media)
        print(f"Выгружаем: {Path(media).stem}")
    except Exception as e:
        print(f"Не удалось выгрузить: {e}")

async def process_videos(app):
    while True:
        if not media_folder.is_dir():
            await asyncio.sleep(2)
            continue

        media_files = [f for f in os.listdir(media_folder) if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm'))]

        if not media_files:
            await asyncio.sleep(2)
            continue

        for media_file in media_files:
            video_path = media_folder / media_file
            thumbnail_path = video_path.with_suffix('.jpg')

            # тут делаем привью
            try:
                clip = VideoFileClip(str(video_path))
                duration = clip.duration
                middle_time = duration / 2
                clip.save_frame(str(thumbnail_path), t=middle_time)
                clip.close()  
            except Exception as e:
                print(f"Не удалось создать превью для {video_path}: {e}")
                continue

            media_group = []
            files_to_remove = [str(video_path), str(thumbnail_path)]
            video_size_mb = video_path.stat().st_size / (1024 * 1024)

            if video_size_mb > MAX_VIDEO_SIZE_MB:
                media_group.append(InputMediaPhoto(media=thumbnail_path))
            
            media_group.append(InputMediaVideo(media=video_path, thumb=str(thumbnail_path)))

            if media_group:
                await send_media_group(app, media_group, files_to_remove)

        await asyncio.sleep(2)

async def main():
    async with Client("my_account", api_id, api_hash) as app:
        await process_videos(app)

asyncio.run(main())
