import asyncio
import subprocess
import sys
import os
from pathlib import Path
import time
from tqdm import tqdm
import config




os.system('cls' if os.name == 'nt' else 'clear')

from pyrogram import Client

def create_session(folder, name, api_id, api_hash):
    # Создаем папку, если она не существует
    if not os.path.exists(folder):
        os.makedirs(folder)
    session_path = os.path.join(folder, name)
    
    app = Client(session_path, api_id, api_hash)
    app.start()
    print(f"Сессия '{name}' создана в папке '{folder}'.")
    app.stop()
api_id = config.api_id                         
api_hash = config.api_hash      

create_session("user_tg_bot", "my_account", api_id, api_hash)
create_session("tg", "my_account", api_id, api_hash)



#ШРИФТ
bold = "\033[1m"
reset = "\033[0m"

# Получение пути к текущему исполняемому файлу Python
python_executable = Path(sys.executable).resolve()

# Путь к файлу сессии в папке tg
session_file = './tg/my_account'

# Функция для чтения каналов из текстового файла
def read_channels_from_file(file_path):
    channels = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                if line.startswith("Chat ID:"):
                    parts = line.split(',')
                    chat_id = int(parts[0].split(': ')[1])
                    chat_title = parts[1].split(': ')[1].strip()
                    if chat_title != "None":  # Фильтруем каналы с None в названии
                        channels.append((chat_id, chat_title))
    except FileNotFoundError:
        print(f"Файл {file_path} не найден.")
    except Exception as e:
        print(f"Ошибка при чтении файла {file_path}: {e}")
    return channels

# Асинхронная функция для выполнения другого скрипта
async def run_script(script):
    script_path = Path(script).resolve() 
    script_dir = script_path.parent 
    try:
        
        # Создаём асинхронный процесс для запуска скрипта
        process = await asyncio.create_subprocess_exec(
            python_executable, script_path,
            cwd=script_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=os.environ.copy()
        )

        # Функция для чтения потока вывода
        async def read_stream(stream, name):
            while True:
                line = await stream.readline()
                if line:
                    if 'user_tg_bot.py' in script:
                        print(f'Выгружаем: {line.decode().strip()}', flush=True)
                else:
                    break

        # Запускаем чтение потоков вывода и ошибок параллельно
        await asyncio.gather(
            read_stream(process.stdout, f'{script} stdout'),
            read_stream(process.stderr, f'{script} stderr')
        )

        # Ожидаем завершения процесса
        await process.wait()
        print(f'{script} завершен', flush=True)

    except Exception as e:
        pass

# Асинхронная функция для выполнения скриптов
async def main(scripts):
    await asyncio.gather(*(run_script(script) for script in scripts))

if __name__ == "__main__":
    print("Обновление списка каналов...")
    result = subprocess.run([sys.executable, 'find_channels.py'], capture_output=True, text=True)
    print("Результат выполнения find_channels.py:")
    print(result.stdout)  
    print(result.stderr)

    # Проверка, что find_channels.py завершился корректно
    if result.returncode != 0:
        print("Ошибка при выполнении find_channels.py")
        sys.exit(1)
    os.system('cls' if os.name == 'nt' else 'clear')

    # Выбор канала
    Channel_choice = '1'
    if Channel_choice == '1':
        NEW_Channel = input("Введите @название канала: ")
        os.environ['MYCHAT_ID'] = NEW_Channel
    else:
        print("Неверный выбор.")
        sys.exit(1)

    # Чтение каналов из файла
    channels = read_channels_from_file('find_chat_id.txt')
    if not channels:
        print("Каналы не найдены.")
        sys.exit(1)

    # Вывод списка каналов для выбора
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f'{bold}Загружаем в “{os.environ["MYCHAT_ID"]}”{reset} ->')
    print("Выберите канал для загрузки:")
    for i, (channel_id, channel_title) in enumerate(channels, start=1):
        print(f"{i}. {channel_title}")

    # Выбор канала
    channel_choice = input("Введите номер канала: ")
    try:
        selected_channel = channels[int(channel_choice) - 1]
        os.environ['CHAT_ID'] = str(selected_channel[0])
    except (IndexError, ValueError):
        print("Неверный выбор.")
        sys.exit(1)

    # Ввод максимального размера файла
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f'{bold}Загружаем в “{os.environ["MYCHAT_ID"]}” из “{selected_channel[1]}”{reset} ->')
    max_file_size_input = input("Введите максимальный размер файла (MB): ")
    try:
        os.environ['MAX_FILE_SIZE'] = str(int(max_file_size_input))
    except ValueError:
        print("Неверный размер файла.")
        sys.exit(1)
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f'{bold}Загружаем в “{os.environ["MYCHAT_ID"]}” из “{selected_channel[1]}” все видео до {os.environ["MAX_FILE_SIZE"]} мб{reset} ->')
    print("Выберите опцию:")
    print("1. Загрузка + Выгрузка")
    print("2. Только Загрузка")  # только app.py
    print("3. Только Выгрузка")  # только user_tg_bot.py

    choice = input("Введите номер опции: ")
    os.system('cls' if os.name == 'nt' else 'clear')

    scripts_to_run = []
    mode = ""
    if choice == '1':
        mode = "Загузка + Выгрузка"
        scripts_to_run = ['tg/app.py', 'user_tg_bot/user_tg_bot.py']
    elif choice == '2':
        mode = "Только Загузка"
        scripts_to_run = ['tg/app.py']
    elif choice == '3':
        mode = "Только Выгрузка"
        scripts_to_run = ['user_tg_bot/user_tg_bot.py']
    else:
        print("Неверный выбор.")
        sys.exit(1)

    chat_name = selected_channel[1]

    print(f'\n\n\n{bold}⚫ Загружаем в “{os.environ["MYCHAT_ID"]}” из “{chat_name}” все видео до {os.environ["MAX_FILE_SIZE"]} мб в режиме “{mode}” ⚫{reset}')
    print("\n\n\n*Если видео не выгружаются:\nПроверьте правильно ли написано название канала пример @test_channel;\nУбедитесь что вы стототе в этом канале;\nУбедитесь что там есть видео этого размера.")

    asyncio.run(main(scripts_to_run))
