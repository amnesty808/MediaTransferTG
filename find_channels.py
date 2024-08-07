import logging
import asyncio
from pyrogram import Client
import config


api_id = config.api_id                         
api_hash = config.api_hash          
session_file = './tg/my_account'


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = Client(session_file, api_id, api_hash)

# ИСКЛЮЧЕНИЯ
excluded_chat_ids = {
        #Тут можно добавить исключения для каналов выгрузки
}

async def list_all_dialogs():
    try:
        await app.start() 
        dialog_ids = set()  #
        dialogs = []

        async for dialog in app.get_dialogs(limit=100):  # Попробуем получить до 100 диалогов за раз
            chat = dialog.chat
            if chat.title is not None and chat.id not in dialog_ids and chat.id not in excluded_chat_ids:

                dialogs.append(dialog)
                dialog_ids.add(chat.id) 
            else:
                logger.info(f"Пропущен чат с ID {chat.id} по причине исключения или повторного добавления.")

        # Записываем данные в файл
        with open('find_chat_id.txt', 'w', encoding='utf-8') as f:
            f.write(f"Account: {api_id}\n")
            f.write(f"Total dialogs: {len(dialogs)}\n")
            for dialog in dialogs:
                chat = dialog.chat
                f.write(f"Chat ID: {chat.id}, Chat Title: {chat.title}, Chat Type: {chat.type}\n")

    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")
    finally:
        await app.stop() 

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(list_all_dialogs())

if __name__ == "__main__":
    main()
