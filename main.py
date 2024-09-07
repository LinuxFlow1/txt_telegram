####--------------------------------####
#--# Author:   by nimida roze       #--#
#--# License:  GNU GPL              #--#
#--# Telegram: @zopav               #--#
####--------------------------------####

import sys
import asyncio
from telethon.sync import TelegramClient
from telethon import events

# Ввод api_id и api_hash
api_id = input("Введите ваш api_id: ")
api_hash = input("Введите ваш api_hash: ")

# Подключение к Telegram
client = TelegramClient('session_name', api_id, api_hash)
client.start()

# Получение информации об аккаунте
entity = client.get_entity("me")
MY_ID = entity.id
print(f"[PROFILE: {entity.first_name} | Id: {MY_ID} | Uname: @{entity.username}]")

# Обработчик команды `.t` для имитации набора текста
@client.on(events.NewMessage(pattern=".t+"))
async def handler(event):
    if event.message.from_id.user_id != MY_ID:
        return

    try:
        if event.message.message.replace(".t ", "") == ".t":
            return

        text      = event.message.message.split(".t ", maxsplit=1)[1]
        orig_text = text
        message   = event.message
        chat      = event.chat_id

        tbp = "" # to be printed
        typing_symbol = "/"
     
        while(tbp != orig_text):
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

edit_heart = '''
1 2 2 1 2 2 1
2 2 2 2 2 2 2
2 2 2 2 2 2 2
1 2 2 2 2 2 1
1 1 2 2 2 1 1
 1 1 1 2 1 1
'''

@client.on(events.NewMessage(pattern=".heart+"))
async def heart_handler(event):
    if event.message.from_id.user_id != MY_ID:
        return
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
    if event.message.from_id.user_id != MY_ID:
        return
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
    if event.message.from_id.user_id != MY_ID:
        return
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

# Alphabet Animation Handler - `.alpha`
alphabet_anim = [
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "J",
    "K",
    "L",
    "M",
    "N",
    "O",
    "P",
    "Q",
    "R",
    "S",
    "T",
    "U",
    "V",
    "W",
    "X",
    "Y",
    "Z",
    "а",
    "б",
    "в",
    "г",
    "д",
    "е",
    "ж",
    "з",
    "и",
    "й",
    "к",
    "л",
    "м",
    "м",
    "н",
    "о",
    "п",
    "с",
    "т",
    "у",
    "ф",
    "х",
    "ц",
    "ч",
    "ш",
    "щ",
    "ъ",
    "ь",
    "ы",
    "э",
    "ю",
    "я",
]

@client.on(events.NewMessage(pattern=".alpha+"))
async def alpha_handler(event):
    if event.message.from_id.user_id != MY_ID:
        return
    try:
        text = event.message.message.replace(".alpha ", "").upper()
        if text == ".alpha":
            text = "ALPHABET ANIMATION"

        message = event.message
        chat = event.chat_id
        tbp = ""  # to be printed
        while tbp != text:
            for char in alphabet_anim:
                tbp += char
                await client.edit_message(chat, message, tbp)
                await asyncio.sleep(0.1)
            tbp = ""
    except Exception as e:
        print(f"[Error] Failed to execute .alpha command: {str(e)}")

@client.on(events.NewMessage(pattern=".gradient+"))
async def gradient_handler(event):
    if event.message.from_id.user_id != MY_ID:
        return
    try:
        text = event.message.message.replace(".gradient ", "")
        if text == ".gradient":
            text = "GRADIENT EFFECT"

        message = event.message
        chat = event.chat_id
        frame_index = 0
        while frame_index != len(gradient_anim):
            await client.edit_message(chat, message, gradient_anim[frame_index])
            await asyncio.sleep(0.20)  # увеличено до 10 секунд
            frame_index += 1
        await client.edit_message(chat, message, text)
    except Exception as e:
        print(f"[Error] Failed to execute .gradient command: {str(e)}")

# Gradient Animation Handler - `.gradient`
gradient_anim = [
    "░▒▓█▓▒░",
    "▒▓█▓▒░▒",
    "▓█▓▒░▒▓",
    "█▓▒░▒▓█",
]

@client.on(events.NewMessage(pattern=".color+"))
async def color_handler(event):
    if event.message.from_id.user_id != MY_ID:
        return
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
        print(f"[Error] Failed to execute .color command: {str(e)}")

# Command `.color` for rainbow effect
color_anim = [
    "🟥", "🟧", "🟨", "🟩", "🟦", "🟪", "🟥"
]
# Обработчик команды `.merc` для мерцания текста
@client.on(events.NewMessage(pattern=".merc+"))
async def merc_handler(event):
    if event.message.from_id.user_id != MY_ID:
        return
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

# Обработчик команды `.wave` для создания волнообразного текста "Привет"
@client.on(events.NewMessage(pattern=".wave+"))
async def wave_handler(event):
    if event.message.from_id.user_id != MY_ID:
        return
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

# Список цветов для эффекта радуги
rainbow_colors = [
    "\033[31m",  # Красный
    "\033[33m",  # Желтый
    "\033[32m",  # Зеленый
    "\033[36m",  # Голубой
    "\033[34m",  # Синий
    "\033[35m",  # Фиолетовый
]

# Сброс цвета
reset_color = "\033[0m"

# Обработчик команды `.rainbow` для создания эффекта радуги
@client.on(events.NewMessage(pattern=".rainbow+"))
async def rainbow_handler(event):
    if event.message.from_id.user_id != MY_ID:
        return
    try:
        # Получаем текст после команды .rainbow
        text = event.message.message.split(".rainbow ", maxsplit=1)[1]
        message = event.message
        chat = event.chat_id

        while True:  # Бесконечный цикл для эффекта радуги
            for i in range(len(rainbow_colors)):
                rainbow_text = ""
                for j, char in enumerate(text):
                    # Меняем цвет каждой буквы
                    rainbow_text += rainbow_colors[(i + j) % len(rainbow_colors)] + char
                rainbow_text += reset_color  # Сбрасываем цвет в конце строки
                await client.edit_message(chat, message, rainbow_text)
                await asyncio.sleep(0.5)  # Скорость смены цветов
    except Exception as e:
        print(f"[Error] Не удалось выполнить команду .rainbow: {str(e)}")

# Обработчик команды `.fall` для создания эффекта падающего текста
@client.on(events.NewMessage(pattern=".fall+"))
async def fall_handler(event):
    if event.message.from_id.user_id != MY_ID:
        return

    try:
        # Извлекаем текст после команды .fall
        text = event.message.message.split(".fall ", maxsplit=1)[1]
        chat = event.chat_id
        
        # Удаляем исходное сообщение с командой
        await event.delete()
        
        # Отправляем первое сообщение с начальным текстом
        sent_message = await client.send_message(chat, text[0])  # Показываем первый символ

        # Цикл для эффекта падения текста
        for i in range(1, len(text) + 1):
            # Формируем падающий текст с накоплением
            fall_text = '\n'.join([text[:j + 1] for j in range(i)])

            # Проверка, чтобы сообщение не было пустым и обновлялось
            if fall_text.strip() and fall_text != sent_message.text:
                await client.edit_message(chat, sent_message.id, fall_text)
            await asyncio.sleep(0.1)  # Настройка скорости падения
    except Exception as e:
        print(f"[Error] Не удалось выполнить команду .fall: {str(e)}")

@client.on(events.NewMessage(pattern=".wave+"))
async def wave_handler(event):
    if event.message.from_id.user_id != MY_ID:
        return

    try:
        text = event.message.message.split(".wave ", maxsplit=1)[1]
        message = event.message
        chat = event.chat_id

        while True:
            for i in range(len(text)):
                wave_text = ''.join(
                    [char.upper() if (j + i) % 2 == 0 else char.lower() for j, char in enumerate(text)]
                )
                await client.edit_message(chat, message, wave_text)
                await asyncio.sleep(0.2)
    except Exception as e:
        print(f"[Error] Не удалось выполнить команду .wave: {str(e)}")

@client.on(events.NewMessage(pattern=".fall+"))
async def fall_handler(event):
    if event.message.from_id.user_id != MY_ID:
        return

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

@client.on(events.NewMessage(pattern=".fireflies+"))
async def fireflies_handler(event):
    if event.message.from_id.user_id != MY_ID:
        return

    try:
        text = event.message.message.split(".fireflies ", maxsplit=1)[1]
        message = event.message
        chat = event.chat_id

        while True:
            fireflies_text = ''.join(
                [char.upper() if random.random() > 0.5 else char.lower() for char in text]
            )
            await client.edit_message(chat, message, fireflies_text)
            await asyncio.sleep(0.3)
    except Exception as e:
        print(f"[Error] Не удалось выполнить команду .fireflies: {str(e)}")
        
# Запуск клиента
client.run_until_disconnected()
