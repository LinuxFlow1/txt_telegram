import os
import sys
import asyncio
from telethon.sync import TelegramClient
from telethon import events

# файл конфигурации
config_file = "config.txt"

# Функция для сохранения данных в файл конфигурации
def save_config(phone_number, api_id, api_hash):
    with open(config_file, "w") as file:
        file.write(f"{phone_number}\\n{api_id}\\n{api_hash}\\n")

# Функция для загрузки данных из файла конфигурации
def load_config():
    if os.path.exists(config_file):
        with open(config_file, "r") as file:
            data = file.read().splitlines()
            if len(data) == 3:
                return data[0], data[1], data[2]
    return None, None, None

# загрузить данные из файла конфигурации
phone_number, api_id, api_hash = load_config()

# Если данные отсутствуют, запросить их у пользователя
if not all([phone_number, api_id, api_hash]):
    print("Введите ваш номер телефона (в международном формате, например, +79991234567): ")
    phone_number = input().strip()
    print("Введите ваш api_id: ")
    api_id = input().strip()
    print("Введите ваш api_hash: ")
    api_hash = input().strip()

    # Сохранить данные в файл конфигурации
    save_config(phone_number, api_id, api_hash)

# Подключение к Telegram
client = TelegramClient('session_name', api_id, api_hash)
client.connect()

if not client.is_user_authorized():
    client.send_code_request(phone_number)
    code = input('Введите код, полученный в Telegram: ')
    client.sign_in(phone_number, code)


# Обработчик команды `.t` для имитации набора текста
@client.on(events.NewMessage(pattern=".t+"))
async def handler(event):
    try:
        text = event.message.message.split(".t ", maxsplit=1)[1]
        orig_text = text
        chat = event.chat_id

        tbp = ""  # to be printed
        typing_symbol = "/"

        # Бот отправляет первое сообщение, которое будет редактироваться
        message = await client.send_message(chat, typing_symbol)

        while tbp != orig_text:
            typing_symbol = "_" if typing_symbol == "/" else "-"
            tbp = tbp + text[0]
            text = text[1:]
            await client.edit_message(chat, message.id, tbp + typing_symbol)
            await asyncio.sleep(0.1)
    except Exception as e:
        print(f"[Error] Не удалось выполнить команду .t: {str(e)}")


# Обработчик команды `.heart` для анимации сердечек
heart_emoji = [
    "✨-💎",
    "✨-🌺",
    "☁️-😘",
    "✨-🌸",
    "🌾-🐸",
    "🔫-💥",
    "☁️-💟",
    "🍀-💖",
    "🌴-🐼",
]

edit_heart = """
1 2 2 1 2 2 1
2 2 2 2 2 2 2
2 2 2 2 2 2 2
1 2 2 2 2 2 1
1 1 2 2 2 1 1
 1 1 1 2 1 1
"""

@client.on(events.NewMessage(pattern=".heart+"))
async def heart_handler(event):
    try:
        chat = event.chat_id
        frame_index = 0

        # Бот отправляет сообщение для анимации
        message = await client.send_message(chat, edit_heart)

        while frame_index != len(heart_emoji):
            animated_text = edit_heart.replace("1", heart_emoji[frame_index].split("-")[0]).replace("2", heart_emoji[frame_index].split("-")[1])
            await client.edit_message(chat, message.id, animated_text)
            await asyncio.sleep(1)
            frame_index += 1
    except Exception as e:
        print(f"[Error] Не удалось выполнить команду .heart: {str(e)}")


# Обработчик команды `.alpha` для анимации текста посимвольно
@client.on(events.NewMessage(pattern=".alpha+"))
async def alpha_handler(event):
    try:
        text = event.message.message.split(".alpha ", maxsplit=1)[1] if ".alpha " in event.message.message else "АЛФАВИТНЫЕ АНИМАЦИИ"
        chat = event.chat_id
        tbp = ""

        # Бот отправляет сообщение для редактирования
        message = await client.send_message(chat, tbp)

        for char in text:
            tbp += char
            await client.edit_message(chat, message.id, tbp)
            await asyncio.sleep(0.1)
    except Exception as e:
        print(f"[Error] Не удалось выполнить команду .alpha: {str(e)}")


# Обработчик команды `.cat` для анимации текста в виде эмодзи котов
cat_emoji = {
    "а": "",
    "б": "🐈",
    "в": "🐾",
    "г": "🐱",
    "д": "🐈",
    "е": "🐾",
    "ё": "🐱",
    "ж": "🐈",
    "з": "🐾",
    "и": "🐱",
    "й": "🐈",
    "к": "🐾",
    "л": "🐱",
    "м": "🐈",
    "н": "🐾",
    "о": "🐱",
    "п": "🐈",
    "р": "🐾",
    "с": "🐱",
    "т": "🐈",
    "у": "🐾",
    "ф": "🐱",
    "х": "🐈",
    "ц": "🐾",
    "ч": "🐱",
    "ш": "🐈",
    "щ": "🐾",
    "ъ": "🐱",
    "ы": "🐈",
    "ь": "🐾",
    "э": "🐱",
    "ю": "🐈",
    "я": ""
}

@client.on(events.NewMessage(pattern=".cat+"))
async def cat_handler(event):
    try:
        text = event.message.message.split(".cat ", maxsplit=1)[1]
        chat = event.chat_id
        tbp = ""

        # Бот отправляет сообщение для редактирования
        message = await client.send_message(chat, tbp)

        for char in text.lower():
            tbp += cat_emoji.get(char, char)
            await client.edit_message(chat, message.id, tbp)
            await asyncio.sleep(0.1)
    except Exception as e:
        print(f"[Error] Не удалось выполнить команду .cat: {str(e)}")


# Обработчик команды `.wave` для волнообразного текста
@client.on(events.NewMessage(pattern=".wave+"))
async def wave_handler(event):
    try:
        text = event.message.message.split(".wave ", maxsplit=1)[1]
        chat = event.chat_id
        message = await client.send_message(chat, text)  # отправляем сообщение для редактирования

        while True:  # Бесконечный цикл для волнообразного эффекта
            for i in range(len(text)):
                wave_text = ""
                for j, char in enumerate(text):
                    if j == i:
                        wave_text += char.upper()
                    else:
                        wave_text += char.lower()
                await client.edit_message(chat, message.id, wave_text)
                await asyncio.sleep(0.1)  # Скорость волны
    except Exception as e:
        print(f"[Error] Не удалось выполнить команду .wave: {str(e)}")


# Обработчик команды `.merc` для мерцания текста
@client.on(events.NewMessage(pattern=".merc+"))
async def merc_handler(event):
    try:
        text = event.message.message.split(".merc ", maxsplit=1)[1]
        chat = event.chat_id
        message = await client.send_message(chat, text)

        while True:  # Бесконечный цикл для мерцания
            await client.edit_message(chat, message.id, text)
            await asyncio.sleep(0.5)  # Пауза для мерцания
            await client.edit_message(chat, message.id, " ")  # Пробел вместо текста
            await asyncio.sleep(0.5)  # Пауза для мерцания
    except Exception as e:
        print(f"[Error] Не удалось выполнить команду .merc: {str(e)}")


# Обработчик команды `.fall` для эффекта падающего текста
@client.on(events.NewMessage(pattern=".fall+"))
async def fall_handler(event):
    try:
        text = event.message.message.split(".fall ", maxsplit=1)[1]
        chat = event.chat_id

        await event.delete()  # Удаляем исходное сообщение с командой
        message = await client.send_message(chat, "‎")  # Невидимый символ для начала анимации

        for i in range(1, len(text) + 1):
            fall_text = '\n'.join([text[:j + 1] for j in range(i)])
            await client.edit_message(chat, message.id, fall_text)
            await asyncio.sleep(0.5)
    except Exception as e:
        print(f"[Error] Не удалось выполнить команду .fall: {str(e)}")


# Запуск клиента
client.run_until_disconnected()
