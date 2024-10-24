import os
import sys
import asyncio
from telethon.sync import TelegramClient
from telethon import events
import random
from telethon.tl.types import PeerUser

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

try:
    entity = client.get_entity(PeerUser(1896098407))
    print(f"пользователь найден: {entity}")
except ValueError as e:
    print(f"Ошибка при получении сущности: {e}")
    
# Функция для получения сущности пользователя
def get_user_entity(identifier):
    try:
        # Получаем сущность пользователя (по ID или username)
        user = client.get_entity(identifier)
        return user
    except RPCError as e:
        print(f"Ошибка RPC при получении сущности пользователя: {e}")
    except Exception as e:
        print(f"Произошла ошибка при получении сущности пользователя: {e}")
    return None
    
# Получение информации об аккаунте
entity = client.get_entity("me")
MY_ID = entity.id
print(f"[PROFILE: {entity.first_name} | Id: {MY_ID} | Uname: @{entity.username}]")

# Обработчик команды `.t` для имитации набора текста
@client.on(events.NewMessage(pattern=".t+"))
async def handler(event):
    try:
        if event.message.message.replace(".t ", "") == ".t":
            return

        text      = event.message.message.split(".t ", maxsplit=1)[1]
        orig_text = text
        message   = event.message
        chat      = event.chat_id

        tbp = "" # to be printed
        typing_symbol = "/"
     
        while tbp != orig_text:
            typing_symbol = "_"
            await client.edit_message(chat, message, tbp + typing_symbol)
            await asyncio.sleep(0.1)

            tbp = tbp + text[0]
            text = text[1:]

            typing_symbol = "-"
            await client.edit_message(chat, message, tbp)
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
        text = event.message.message.replace(".heart ", "")
        if text == ".heart":
            message = event.message
            chat = event.chat_id
            frame_index = 0
            while frame_index != len(heart_emoji):
                await client.edit_message(chat, message, edit_heart.replace("1", heart_emoji[frame_index].split("-")[0])
                                                                .replace("2", heart_emoji[frame_index].split("-")[1]))
                await asyncio.sleep(1)
                frame_index += 1
            await client.edit_message(chat, message, text)
    except Exception as e:
        print(f"[Error] Не удалось выполнить команду .heart: {str(e)}")

# Обработчик команды `.alpha` для анимации текста посимвольно (поддержка русского алфавита)
@client.on(events.NewMessage(pattern=".alpha+"))
async def alpha_handler(event):
    try:
        text = event.message.message.split(".alpha ", maxsplit=1)
        if len(text) > 1:
            text = text[1]
        else:
            text = "АЛФАВИТНЫЕ АНИМАЦИИ"

        message = event.message
        chat = event.chat_id
        tbp = ""  # to be напечатано

        for char in text:
            tbp += char
            await client.edit_message(chat, message, tbp)
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
        message = event.message
        chat = event.chat_id
        tbp = ""

        for char in text.lower():
            tbp += cat_emoji.get(char, char)  # заменяем буквы на эмодзи или оставляем их без изменений
            await client.edit_message(chat, message, tbp)
            await asyncio.sleep(0.1)
    except Exception as e:
        print(f"[Error] Не удалось выполнить команду .cat: {str(e)}")

# Обработчик команды `.wave` для создания волнообразного текста
@client.on(events.NewMessage(pattern=".wave+"))
async def wave_handler(event):
    try:
        text = event.message.message.split(".wave ", maxsplit=1)[1]
        message = event.message
        chat = event.chat_id
        
        while True:  # Бесконечный цикл для волнообразного эффекта
            for i in range(len(text)):
                wave_text = ""
                for j, char in enumerate(text):
                    if j == i:
                        wave_text += char.upper()
                    else:
                        wave_text += char.lower()
                await client.edit_message(chat, message, wave_text)
                await asyncio.sleep(0.1)  # Скорость волны
    except Exception as e:
        print(f"[Error] Не удалось выполнить команду .wave: {str(e)}")


# Обработчик команды `.merc` для мерцания текста
@client.on(events.NewMessage(pattern=".merc+"))
async def merc_handler(event):
    try:
        text = event.message.message.split(".merc ", maxsplit=1)[1]
        message = event.message
        chat = event.chat_id
        while True:  # Бесконечный цикл для мерцания
            await client.edit_message(chat, message, text)
            await asyncio.sleep(0.5)  # Пауза для мерцания
            await client.edit_message(chat, message, " ")  # Пробел вместо текста
            await asyncio.sleep(0.5)  # Пауза для мерцания
    except Exception as e:
        print(f"[Error] Не удалось выполнить команду .merc: {str(e)}")


# Обработчик команды `.gradient` для градиентной анимации
gradient_anim = [
    "░▒▓█▓▒░",
    "▒▓█▓▒░▒",
    "▓█▓▒░▒▓",
    "█▓▒░▒▓█",
]

@client.on(events.NewMessage(pattern=".gradient+"))
async def gradient_handler(event):
    try:
        text = event.message.message.replace(".gradient ", "")
        if text == ".gradient":
            text = "GRADIENT EFFECT"

        message = event.message
        chat = event.chat_id
        frame_index = 0
        while frame_index != len(gradient_anim):
            await client.edit_message(chat, message, gradient_anim[frame_index])
            await asyncio.sleep(0.10)
            frame_index += 1
        await client.edit_message(chat, message, text)
    except Exception as e:
        print(f"[Error] Не удалось выполнить команду .gradient: {str(e)}")


# Обработчик команды `.color` для анимации цвета
color_anim = [
    "🟥", "🟧", "🟨", "🟩", "🟦", "🟪", "🟥"
]

@client.on(events.NewMessage(pattern=".color+"))
async def color_handler(event):
    try:
        text = event.message.message.replace(".color ", "")
        if text == ".color":
            text = "RAINBOW EFFECT"

        message = event.message
        chat = event.chat_id
        tbp = ""  # to be printed
        for color in color_anim:
            tbp += color
            await client.edit_message(chat, message, tbp)
            await asyncio.sleep(0.5)  # уменьшил интервал для плавности анимации
        await client.edit_message(chat, message, text)
    except Exception as e:
        print(f"[Error] Не удалось выполнить команду .color: {str(e)}")


# Обработчик команды `.fall` для эффекта падающего текста
@client.on(events.NewMessage(pattern=".fall+"))
async def fall_handler(event):
    try:
        text = event.message.message.split(".fall ", maxsplit=1)[1]
        chat = event.chat_id
        
        await event.delete()  # Удаляем исходное сообщение с командой
        
        sent_message = await client.send_message(chat, "‎")  # Невидимый символ для начала анимации

        for i in range(1, len(text) + 1):
            fall_text = '\n'.join([text[:j + 1] for j in range(i)])
            
            if fall_text.strip() and fall_text != sent_message.text:
                await client.edit_message(chat, sent_message.id, fall_text)
            await asyncio.sleep(0.5)
    except Exception as e:
        print(f"[Error] Не удалось выполнить команду .fall: {str(e)}")

# Запуск клиента
client.run_until_disconnected()
