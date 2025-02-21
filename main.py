import cv2
import numpy as np
import os
import asyncio
import random
import requests
from telethon import events, Button
import tempfile
import math
import subprocess
import json
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from telethon import TelegramClient
from telethon.errors import FloodWaitError, ChatAdminRequiredError
from collections import deque
from pyfiglet import Figlet

# Конфигурация
CONFIG_FILE = "tg_config.json"

class ConfigManager:
    """Управление конфигурацией бота."""
    @staticmethod
    def save(phone, api_id, api_hash, disable_animations=False):
        """Сохраняет конфигурацию в файл."""
        config = {
            "phone": phone,
            "api_id": api_id,
            "api_hash": api_hash,
            "disable_animations": disable_animations
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f)

    @staticmethod
    def load():
        """Загружает конфигурацию из файла."""
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                return (
                    config.get("phone"),
                    config.get("api_id"),
                    config.get("api_hash"),
                    config.get("disable_animations", False)
                )
        except (FileNotFoundError, json.JSONDecodeError):
            return None, None, None, False

async def setup_client():
    """Настройка клиента Telegram."""
    phone, api_id, api_hash, disable_animations = ConfigManager.load()
    if not all([phone, api_id, api_hash]):
        phone = input("📱 Введите номер телефона: ").strip()
        api_id = input("🔑 Введите API ID: ").strip()
        if not api_id.isdigit():
            raise ValueError("API ID должен быть числом.")
        api_id = int(api_id)
        api_hash = input("💎 Введите API HASH: ").strip()
        ConfigManager.save(phone, api_id, api_hash, disable_animations=False)
    return TelegramClient('tg_session', api_id, api_hash), phone, disable_animations

client, phone, DISABLE_ANIMATIONS = asyncio.run(setup_client())
SELF_ID = None  # Инициализируется при запуске бота

# Константы для игры "Бегущий динозавр"
VIEW_WIDTH = 30
WORLD_WIDTH = 1000
JUMP_HEIGHT = 4
GRAVITY = 0.5
OBSTACLES = ['🌵', '🦖', '💨']
GROUND = '═'

# Константы для анимации "Cubbies Ripples"
CUBE_CHARS = ["▀", "▄", "■", "▌", "▐", "▖", "▗", "▘", "▙", "▚", "▛", "▜", "▝", "▞", "▟"]
RIPPLE_WIDTH = 20
RIPPLE_HEIGHT = 10
RIPPLE_SPEED = 0.2

# Состояния игр и анимаций
active_games = {}

# Константы для анимации .heart
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

# Шаблоны и уровни для анимаций
SPIRAL_TEMPLATE = """
4 4 4 4 4 4 4 4 4 4 4 4
4 3 3 3 3 3 3 3 3 3 3 4
4 3 2 2 2 2 2 2 2 2 3 4
4 3 2 1 1 1 1 1 1 2 3 4
4 3 2 1 0 0 0 0 1 2 3 4
4 3 2 1 0 0 0 0 1 2 3 4
4 3 2 1 0 0 0 0 1 2 3 4
4 3 2 1 1 1 1 1 1 2 3 4
4 3 2 2 2 2 2 2 2 2 3 4
4 3 3 3 3 3 3 3 3 3 3 4
4 4 4 4 4 4 4 4 4 4 4 4
"""
SPIRAL_LEVELS = {
    0: "•",  # Центр
    1: "░",  # Внутренний слой
    2: "▒",  # Средний слой
    3: "▓",  # Внешний слой
    4: " "   # Фон
}

WAVE_TEMPLATE = """
0 1 2 3 4 5 6 7 8 9
0 1 2 3 4 5 6 7 8 9
0 1 2 3 4 5 6 7 8 9
0 1 2 3 4 5 6 7 8 9
0 1 2 3 4 5 6 7 8 9
0 1 2 3 4 5 6 7 8 9
0 1 2 3 4 5 6 7 8 9
0 1 2 3 4 5 6 7 8 9
0 1 2 3 4 5 6 7 8 9
0 1 2 3 4 5 6 7 8 9
"""
WAVE_LEVELS = {
    0: "≈", 1: "~", 2: "⁓", 3: "∿",
    4: "·", 5: " ", 6: "·", 7: "∿",
    8: "⁓", 9: "~"
}

# Класс для игры "Бегущий динозавр"
class DinoGame:
    """Класс для управления игрой 'Бегущий динозавр'."""
    def __init__(self, chat_id):
        """Инициализация игры.
        :param chat_id: ID чата, в котором запущена игра.
        """
        self.chat_id = chat_id
        self.is_running = True
        self.dino_pos = 0  # Позиция динозавра по вертикали
        self.dino_vel = 0  # Скорость динозавра
        self.obstacles = deque()  # Очередь препятствий
        self.score = 0  # Счет игры
        self.message = None  # Сообщение с игровым полем

    async def game_loop(self):
        """Основной игровой цикл."""
        try:
            # Создаем начальное игровое поле
            self.message = await client.send_message(
                self.chat_id,
                self._render_frame(),
                buttons=[
                    [Button.inline("🦘 Прыжок", b"jump")],
                    [Button.inline("⛔ Остановить", b"stop")]
                ]
            )
            while self.is_running:
                # Обновляем состояние игры
                self._update_game_state()
                # Рендерим кадр
                await self.message.edit(self._render_frame())
                # Ждем перед следующим кадром
                await asyncio.sleep(0.5)
            # Завершаем игру
            await self.game_over()
        except Exception as e:
            print(f"Ошибка в игровом цикле: {e}")

    def _update_game_state(self):
        """Обновляет состояние игры."""
        # Гравитация
        self.dino_pos += self.dino_vel
        self.dino_vel += GRAVITY
        # Ограничение на землю
        if self.dino_pos < 0:
            self.dino_pos = 0
            self.dino_vel = 0
        # Генерация новых препятствий
        if random.random() < 0.2:  # 20% шанс на создание препятствия
            self.obstacles.append(random.choice(OBSTACLES))
        # Движение препятствий
        if len(self.obstacles) > 0:
            self.obstacles.popleft()
        # Проверка столкновений
        if len(self.obstacles) > 0 and self.obstacles[0] != ' ' and self.dino_pos == 0:
            self.is_running = False  # Игра окончена
        # Увеличение счета
        self.score += 1

    def _render_frame(self):
        """Рендерит текущий кадр игры."""
        frame = []
        # Верхняя часть (небо)
        for _ in range(JUMP_HEIGHT):
            frame.append(" " * VIEW_WIDTH)
        # Линия с динозавром и препятствиями
        dino_line = list(" " * VIEW_WIDTH)
        if self.dino_pos == 0:
            dino_line[0] = "🦖"  # Динозавр на земле
        else:
            dino_line[0] = "🦘"  # Динозавр в прыжке
        # Добавляем препятствия
        for i, obstacle in enumerate(self.obstacles):
            if i < VIEW_WIDTH:
                dino_line[i] = obstacle
        frame.append("".join(dino_line))
        # Земля
        frame.append(GROUND * VIEW_WIDTH)
        # Счет
        frame.append(f"Счет: {self.score}")
        return "\n".join(frame)

    async def jump(self):
        """Обрабатывает прыжок динозавра."""
        if self.dino_pos == 0:  # Динозавр может прыгать только с земли
            self.dino_vel = -JUMP_HEIGHT

    async def game_over(self):
        """Завершает игру."""
        await self.message.edit(f"Игра окончена! Ваш счет: {self.score}")
        del active_games[self.chat_id]  # Удаляем игру из активных

# Обработчики команд
@client.on(events.NewMessage(pattern=r"\.t\s.+"))
async def typewriter_handler(event):
    """Эффект печатающей машинки."""
    try:
        if DISABLE_ANIMATIONS and event.sender_id != SELF_ID:
            return
        await event.delete()  # Удаляем команду
        text = event.text.split(".t ", 1)[1]
        msg = await event.respond("_")  # Новое сообщение
        buffer = ""
        for char in text:
            buffer += char
            try:
                await msg.edit(buffer + "_")
            except FloodWaitError as e:
                print(f"FloodWait: Ожидаем {e.seconds} сек...")
                await asyncio.sleep(e.seconds)
                await msg.edit(buffer + "_")
            await asyncio.sleep(0.3)
        await msg.edit(buffer)
    except Exception as e:
        print(f"Ошибка в .t: {e}")

@client.on(events.NewMessage(pattern=r"\.ascii\s.+"))
async def ascii_handler(event):
    """Преобразует текст в ASCII-арт."""
    try:
        if DISABLE_ANIMATIONS and event.sender_id != SELF_ID:
            return
        await event.delete()  # Удаляем команду
        text = event.text.split(maxsplit=1)[1]
        figlet = Figlet(font='slant')
        ascii_art = figlet.renderText(text)
        await event.respond(f"```\n{ascii_art}\n```")  # Новое сообщение
    except Exception as e:
        print(f"ASCII error: {e}")

@client.on(events.NewMessage(pattern=r"\.cosmic\s.+"))
async def cosmic_handler(event):
    """Галактическая анимация."""
    try:
        if DISABLE_ANIMATIONS and event.sender_id != SELF_ID:
            return
        await event.delete()  # Удаляем команду
        text = event.text.split(maxsplit=1)[1]
        msg = await event.respond("🌀 Инициализация...")  # Новое сообщение
        await cosmic_explosion_effect(msg, text)
    except Exception as e:
        print(f"Error: {e}")

@client.on(events.NewMessage(pattern=r"\.cubbies"))
async def cubbies_handler(event):
    """Анимация 'Cubbies Ripples'."""
    try:
        if DISABLE_ANIMATIONS and event.sender_id != SELF_ID:
            return
        await event.delete()  # Удаляем команду
        animation = RippleAnimation(event.chat_id)
        asyncio.create_task(animation.run())
    except Exception as e:
        print(f"Ошибка: {e}")

@client.on(events.NewMessage(pattern='/rundino'))
async def start_game(event):
    """Запуск игры 'Бегущий динозавр'."""
    try:
        if DISABLE_ANIMATIONS and event.sender_id != SELF_ID:
            return
        await event.delete()  # Удаляем команду
        chat_id = event.chat_id
        if chat_id in active_games:
            warn_msg = await event.respond("❗ Игра уже запущена!")
            await asyncio.sleep(3)
            await warn_msg.delete()
            return
        game = DinoGame(chat_id)
        active_games[chat_id] = game
        asyncio.create_task(game.game_loop())
    except Exception as e:
        print(f"Ошибка в /rundino: {e}")

@client.on(events.CallbackQuery)
async def handle_callback(event):
    """Обработка callback-запросов."""
    game = active_games.get(event.chat_id)
    if not game:
        return
    if event.data == b'jump':
        await game.jump()
    elif event.data == b'stop':
        game.is_running = False
        await game.game_over()

@client.on(events.NewMessage(pattern=r"\.heart+"))
async def heart_handler(event):
    """Анимация сердца."""
    try:
        if DISABLE_ANIMATIONS and event.sender_id != SELF_ID:
            return
        await event.delete()  # Удаляем команду
        chat = event.chat_id
        frame_index = 0
        # Бот отправляет сообщение для анимации
        message = await client.send_message(chat, edit_heart)
        while frame_index < len(heart_emoji):
            animated_text = edit_heart.replace("1", heart_emoji[frame_index].split("-")[0]).replace("2", heart_emoji[frame_index].split("-")[1])
            await client.edit_message(chat, message.id, animated_text)
            await asyncio.sleep(1)
            frame_index += 1
    except Exception as e:
        print(f"[Error] Не удалось выполнить команду .heart: {str(e)}")

@client.on(events.NewMessage(pattern=r"\.wave+"))
async def wave_handler(event):
    """Волнообразный эффект."""
    try:
        if DISABLE_ANIMATIONS and event.sender_id != SELF_ID:
            return
        await event.delete()  # Удаляем команду
        text = event.message.message.split(".wave ", maxsplit=1)[1]
        chat = event.chat_id
        message = await client.send_message(chat, text)  # отправляем сообщение для редактирования
        while True:  # Бесконечный цикл для волнообразного эффекта
            for i in range(len(text)):
                wave_text = ""
                for j, char in enumerate(text):
                    wave_text += char.upper() if j == i else char.lower()
                await client.edit_message(chat, message.id, wave_text)
                await asyncio.sleep(0.1)  # Скорость волны
    except Exception as e:
        print(f"[Error] Не удалось выполнить команду .wave: {str(e)}")

@client.on(events.NewMessage(pattern=r"\.merc+"))
async def merc_handler(event):
    """Мерцание текста."""
    try:
        if DISABLE_ANIMATIONS and event.sender_id != SELF_ID:
            return
        await event.delete()  # Удаляем команду
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

@client.on(events.NewMessage(pattern=r"\.spiral"))
async def spiral_handler(event):
    """Анимация вращающейся спирали."""
    try:
        if DISABLE_ANIMATIONS and event.sender_id != SELF_ID:
            return
        await event.delete()
        chat = event.chat_id
        message = await client.send_message(chat, "🌀 Запуск спирали...")
        # Парсинг шаблона
        template = [row.strip().split() for row in SPIRAL_TEMPLATE.strip().split('\n')]
        rows = len(template)
        cols = len(template[0])
        # Параметры анимации
        frames = 36  # Полный оборот
        delay = 0.1
        for frame in range(frames):
            # Создание кадра
            rotated = []
            shift = frame % cols
            for row in template:
                # Циклический сдвиг
                new_row = row[-shift:] + row[:-shift]
                # Преобразование в символы
                rotated_row = [SPIRAL_LEVELS[int(n)] for n in new_row]
                rotated.append(" ".join(rotated_row))
            await message.edit(f"```\n{chr(10).join(rotated)}\n```")
            await asyncio.sleep(delay)
        await message.edit("✨ Спираль завершена!")
    except Exception as e:
        print(f"Spiral error: {e}")

@client.on(events.NewMessage(pattern=r"\.wave_anim"))
async def wave_anim_handler(event):
    """Анимация волны."""
    try:
        if DISABLE_ANIMATIONS and event.sender_id != SELF_ID:
            return
        await event.delete()
        chat = event.chat_id
        message = await client.send_message(chat, "🌊 Запуск волны...")
        # Парсинг шаблона
        template = [list(map(int, row.strip().split())) for row in WAVE_TEMPLATE.strip().split('\n')]
        rows = len(template)
        cols = len(template[0])
        # Параметры анимации
        frames = 20
        delay = 0.15
        for frame in range(frames):
            # Генерация кадра
            animated = []
            phase = frame % len(WAVE_LEVELS)
            for row in template:
                # Применение фазового сдвига
                new_row = [str((n + phase) % len(WAVE_LEVELS)) for n in row]
                # Двойной волновой эффект
                shifted_row = new_row[frame%cols:] + new_row[:frame%cols]
                # Преобразование в символы
                wave_row = [WAVE_LEVELS[int(n)] for n in shifted_row]
                animated.append(" ".join(wave_row))
            await message.edit(f"```\n{chr(10).join(animated)}\n```")
            await asyncio.sleep(delay)
        await message.edit("✨ Волна завершена!")
    except Exception as e:
        print(f"Wave error: {e}")

@client.on(events.NewMessage(pattern=r"\.fractal"))
async def fractal_handler(event):
    """Анимация фрактала (треугольник Серпинского)."""
    try:
        if DISABLE_ANIMATIONS and event.sender_id != SELF_ID:
            return
        await event.delete()  # Удаляем команду
        chat = event.chat_id
        message = await client.send_message(chat, "🌀 Запуск фрактала...")
        # Параметры фрактала
        size = 16
        frames = 20
        delay = 0.2
        def generate_fractal(level):
            if level == 0:
                return ["#"]
            else:
                smaller = generate_fractal(level - 1)
                return [row + " " * (2 ** (level - 1)) + row for row in smaller] + \
                       [row + row for row in smaller]
        for frame in range(frames):
            fractal = generate_fractal(min(frame, 4))  # Ограничиваем глубину фрактала
            fractal_text = "\n".join(fractal)
            await client.edit_message(chat, message.id, f"```\n{fractal_text}\n```")
            await asyncio.sleep(delay)
        await client.edit_message(chat, message.id, "✨ Фрактал завершён!")
    except Exception as e:
        print(f"[Error] Не удалось выполнить команду .fractal: {str(e)}")

@client.on(events.NewMessage(pattern=r"\.speak\s.+"))
async def text_to_speech_handler(event):
    """Озвучивание текста."""
    try:
        if DISABLE_ANIMATIONS and event.sender_id != SELF_ID:
            return
        await event.delete()  # Удаляем команду
        text = event.text.split(".speak ", 1)[1]
        # Сохраняем текст в файл
        with open("tts.txt", "w", encoding="utf-8") as f:
            f.write(text)
        # Вызываем Termux API для воспроизведения
        subprocess.run(["termux-tts-speak", "-f", "tts.txt"])
        # Уведомление об успехе
        msg = await event.respond("🔊 Текст озвучен!")
        await asyncio.sleep(3)
        await msg.delete()
    except Exception as e:
        error_msg = await event.respond(f"❌ Ошибка: {str(e)}")
        await asyncio.sleep(5)
        await error_msg.delete()

@client.on(events.NewMessage(pattern=r"\.read"))
async def voice_message_handler(event):
    """Озвучивание текста из сообщения."""
    try:
        if DISABLE_ANIMATIONS and event.sender_id != SELF_ID:
            return
        # Удаляем команду
        await event.delete()
        # Проверяем, что это ответ на сообщение
        if not event.is_reply:
            msg = await event.respond("❗ Ответьте на сообщение командой .read")
            await asyncio.sleep(3)
            await msg.delete()
            return
        # Получаем исходное сообщение
        reply_msg = await event.get_reply_message()
        # Извлекаем текст
        if not reply_msg.text:
            msg = await event.respond("❌ В сообщении нет текста для озвучки")
            await asyncio.sleep(3)
            await msg.delete()
            return
        text = reply_msg.text
        # Озвучиваем через Termux
        subprocess.run(["termux-tts-speak", text])
        # Подтверждение с автоудалением
        msg = await event.respond("🔊 Сообщение озвучено!")
        await asyncio.sleep(3)
        await msg.delete()
    except Exception as e:
        error_msg = await event.respond(f"❌ Ошибка: {str(e)}")
        await asyncio.sleep(5)
        await error_msg.delete()

@client.on(events.NewMessage(pattern=r"\.foto_ascii(?:\s+(\d+))? ?"))
async def foto_ascii_handler(event):
    """Улучшенный ASCII-арт с акцентом на детали и яркость."""
    try:
        if DISABLE_ANIMATIONS and event.sender_id != SELF_ID:
            return
        if not event.is_reply:
            response = await event.reply("❗ **Ответьте на изображение!**")
            await asyncio.sleep(2)
            await response.delete()
            return
        reply_msg = await event.get_reply_message()
        # Проверка типа контента
        if not reply_msg.photo and not (reply_msg.document and reply_msg.document.mime_type.startswith('image/')):
            response = await event.reply("❌ **Это не изображение!**")
            await asyncio.sleep(2)
            await response.delete()
            return
        # Параметры обработки
        width = int(event.pattern_match.group(1)) if event.pattern_match.group(1) else 200
        width = min(width, 300)  # Защита от перегрузки
        msg_progress = await event.reply("🔍 **Обработка деталей...**")
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_input_path = os.path.join(temp_dir, "input.jpg")
            await reply_msg.download_media(temp_input_path)
            try:
                # Улучшенная конвертация
                ascii_data = await _enhanced_image_processing(temp_input_path, width)
                output_path = await _render_high_contrast(ascii_data)
                await msg_progress.delete()
                await event.reply(
                    file=output_path,
                    message="🎆 **Яркий ASCII-арт** (HD)"
                )
            except Exception as e:
                await msg_progress.edit(f"❌ **Ошибка:** `{str(e)}`")
                await asyncio.sleep(5)
    except Exception as e:
        await event.reply(f"💥 **Критическая ошибка:** `{str(e)}`")

async def _enhanced_image_processing(image_path, width):
    """Улучшенная обработка с сохранением теней."""
    with Image.open(image_path) as img:
        # Конвертация в RGB для работы с цветами
        img = img.convert("RGB")
        width = min(width, img.width)
        aspect = img.height / img.width
        height = int(width * aspect * 0.6)  # Оптимальное соотношение
        img = img.resize((width, height), Image.LANCZOS)  # Улучшенное сглаживание
        pixels = img.getdata()
        # Расширенная палитра символов для теней
        ASCII_CHARS = "@%#*+=-:. "  # Детализация теней
        data = {"text": [], "colors": [], "width": width, "height": height}  # Добавлены width и height
        for y in range(height):
            row = []
            colors = []
            for x in range(width):
                r, g, b = pixels[y * width + x]
                # Усиление яркости и контраста
                r = min(r * 1.2, 255)
                g = min(g * 1.2, 255)
                b = min(b * 1.2, 255)
                # Новая формула яркости с акцентом на тени
                brightness = (0.299 * r + 0.587 * g + 0.114 * b) / 255
                idx = int(brightness * (len(ASCII_CHARS) - 1))
                row.append(ASCII_CHARS[idx])
                colors.append((int(r), int(g), int(b)))
            data["text"].append("".join(row))
            data["colors"].append(colors)
        return data

async def _render_high_contrast(ascii_data, font_size=12):
    """Рендер с высоким контрастом."""
    try:
        # Попытка загрузить шрифт
        try:
            font = ImageFont.truetype("DejaVuSansMono-Bold.ttf", font_size)
        except IOError:
            # Если шрифт не найден, используем стандартный
            font = ImageFont.load_default()
        bbox = font.getbbox("█")
        char_width, char_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
        # Создаем изображение с серым фоном для контраста
        img = Image.new(
            "RGB",
            (ascii_data["width"] * char_width, ascii_data["height"] * char_height),
            (40, 40, 40)  # Темно-серый фон
        )
        draw = ImageDraw.Draw(img)
        # Отрисовка с эффектом свечения
        for y, (line, colors) in enumerate(zip(ascii_data["text"], ascii_data["colors"])):
            for x, (char, color) in enumerate(zip(line, colors)):
                draw.text(
                    (x * char_width, y * char_height),
                    char,
                    font=font,
                    fill=color
                )
        # Резкость через фильтр
        img = img.filter(ImageFilter.SHARPEN)
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            img.save(f, "PNG", quality=95, optimize=True)
            return f.name
    except Exception as e:
        raise Exception(f"Render error: {str(e)}")

TMDB_API_KEY = "YOUR_TMDB_API_KEY"

# Словарь для активных киносеансов (ключ — chat_id)
active_film_players = {}

# Режимы ожидания плеера:
# "Awaiting URL" – плеер ждёт прямой URL от пользователя
# "Awaiting Search Query" – плеер ждёт текст для поиска фильма по TMDb

class FilmPlayer:
    """Интерактивный плеер с расширенным функционалом и интеграцией с TMDb и lampa.web."""
    def __init__(self, chat_id, message):
        self.chat_id = chat_id
        self.message = message
        self.url = None
        self.title = None
        self.state = "Stopped"  # Возможные состояния: Stopped, Playing, Paused, Awaiting URL, Awaiting Search Query
        self.current_time = 0  # Текущее время воспроизведения (в секундах)
        self.quality = "720p"   # Качество видео
        self.muted = False      # Состояние звука
        self._playing_task = None

    def get_progress_bar(self, length=20):
        """Возвращает строку прогресс-бара (максимум 60 сек)."""
        total = 60
        filled = int((self.current_time / total) * length)
        bar = "█" * filled + "░" * (length - filled)
        return bar

    def get_buttons(self):
        """Формирует inline‑клавиатуру плеера с четырьмя рядами кнопок."""
        # Первый ряд – базовое управление и перемотка:
        row1 = [
            Button.inline("◀️ 10s", b"film_rewind"),
            Button.inline("▶️ Play", b"film_play"),
            Button.inline("⏸ Pause", b"film_pause"),
            Button.inline("10s ▶️", b"film_forward"),
            Button.inline("⏹ Stop", b"film_stop")
        ]
        # Второй ряд – ввод ссылки и поиск фильма:
        row2 = [
            Button.inline("🔗 Ввести ссылку", b"film_enter_url"),
            Button.inline("🔍 Поиск фильма", b"film_search")
        ]
        # Третий ряд – выбор качества:
        row3 = [
            Button.inline("480p", b"film_quality_480"),
            Button.inline("720p", b"film_quality_720"),
            Button.inline("1080p", b"film_quality_1080")
        ]
        # Четвёртый ряд – опция звука:
        row4 = [
            Button.inline("🔊" if not self.muted else "🔇", b"film_toggle_sound")
        ]
        return [row1, row2, row3, row4]

    async def update_message(self):
        """Обновляет сообщение плеера с текущим статусом и клавиатурой."""
        text = "🎬 **Кинотеатр**\n\n"
        text += f"Фильм: {self.title if self.title else 'Не выбран'}\n"
        text += f"URL: {self.url if self.url else 'Отсутствует'}\n"
        text += f"Состояние: {self.state}\n"
        text += f"Качество: {self.quality}\n"
        text += f"Звук: {'Отключен' if self.muted else 'Включен'}\n"
        text += f"Время: {self.current_time} сек\n"
        text += f"Прогресс: {self.get_progress_bar()}\n\n"
        if self.state in ["Awaiting URL", "Awaiting Search Query"]:
            text += "Ожидается ввод от пользователя..."
        else:
            text += "Ниже окно просмотра с кнопками управления:"
        buttons = self.get_buttons()
        await self.message.edit(text, buttons=buttons)

    async def play(self):
        """Запускает воспроизведение фильма."""
        if not self.url:
            await self.message.edit(
                "❗ Фильм не выбран! Сначала введите ссылку или выполните поиск.",
                buttons=[
                    [Button.inline("🔗 Ввести ссылку", b"film_enter_url"),
                     Button.inline("🔍 Поиск фильма", b"film_search")]
                ]
            )
            return
        self.state = "Playing"
        await self.update_message()
        if self._playing_task and not self._playing_task.done():
            self._playing_task.cancel()
        self._playing_task = asyncio.create_task(self.simulate_play())

    async def pause(self):
        """Приостанавливает воспроизведение."""
        if self.state == "Playing":
            self.state = "Paused"
            await self.update_message()

    async def stop(self):
        """Останавливает воспроизведение и сбрасывает время."""
        self.state = "Stopped"
        self.current_time = 0
        await self.update_message()

    async def forward(self, seconds=10):
        """Перематывает вперёд."""
        self.current_time += seconds
        if self.current_time > 60:
            self.current_time = 60
        await self.update_message()

    async def rewind(self, seconds=10):
        """Перематывает назад."""
        self.current_time -= seconds
        if self.current_time < 0:
            self.current_time = 0
        await self.update_message()

    async def toggle_sound(self):
        """Переключает состояние звука."""
        self.muted = not self.muted
        await self.update_message()

    async def simulate_play(self):
        """Симулирует воспроизведение — увеличивает время каждую секунду до 60 сек."""
        try:
            while self.state == "Playing":
                await asyncio.sleep(1)
                self.current_time += 1
                if self.current_time >= 60:
                    self.state = "Stopped"
                    self.current_time = 60
                    await self.update_message()
                    break
                await self.update_message()
        except asyncio.CancelledError:
            pass

# Функция поиска фильмов через TMDb
def search_movie_tmdb(query):
    url = "https://api.themoviedb.org/3/search/movie"
    params = {"api_key": TMDB_API_KEY, "query": query, "language": "ru-RU"}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data.get("results", [])
    return []

# Функция получения трейлера фильма через TMDb
def get_movie_trailer(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos"
    params = {"api_key": TMDB_API_KEY, "language": "ru-RU"}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        for video in data.get("results", []):
            if video.get("site") == "YouTube" and video.get("type") == "Trailer":
                return f"https://youtu.be/{video.get('key')}"
    return None

# Функция получения подробной информации и постера из lampa.web API
def get_movie_details_lampa(movie_id):
    """
    Предполагаем, что API lampa.web находится по адресу:
      https://lampa.example.com/api/movie/{movie_id}
    и возвращает JSON с ключами 'title' и 'poster'.
    """
    url = f"https://lampa.example.com/api/movie/{movie_id}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data  # Ожидаем, что data содержит 'title' и 'poster'
    except Exception as e:
        print(f"Ошибка при получении данных из lampa.web: {e}")
    return None

# Команда для запуска плеера
@client.on(events.NewMessage(pattern=r"\.film"))
async def film_handler(event):
    try:
        if DISABLE_ANIMATIONS and event.sender_id != SELF_ID:
            return
        await event.delete()
        chat = event.chat_id
        message = await client.send_message(chat, "🎬 Инициализация плеера...")
        film_player = FilmPlayer(chat, message)
        active_film_players[chat] = film_player
        await film_player.update_message()
    except Exception as e:
        print(f"Ошибка в .film: {e}")

# Обработка inline‑кнопок плеера
@client.on(events.CallbackQuery)
async def film_callback_handler(event):
    chat = event.chat_id
    if chat not in active_film_players:
        return
    film_player = active_film_players[chat]
    data = event.data.decode('utf-8')
    if data == "film_play":
        await film_player.play()
    elif data == "film_pause":
        await film_player.pause()
    elif data == "film_stop":
        await film_player.stop()
    elif data == "film_forward":
        await film_player.forward(10)
    elif data == "film_rewind":
        await film_player.rewind(10)
    elif data == "film_toggle_sound":
        await film_player.toggle_sound()
        await event.answer("Звук переключён")
    elif data == "film_enter_url":
        film_player.state = "Awaiting URL"
        await film_player.update_message()
        await event.answer("Отправьте ссылку на фильм в чат")
    elif data == "film_search":
        film_player.state = "Awaiting Search Query"
        await film_player.update_message()
        await event.answer("Введите название фильма для поиска")
    elif data.startswith("film_select_"):
        # Обработка выбора фильма из результатов поиска.
        movie_id = data.split("_")[-1]
        trailer_url = get_movie_trailer(movie_id)
        details = get_movie_details_lampa(movie_id)
        if details:
            poster_url = details.get("poster")
            title = details.get("title", f"Фильм {movie_id}")
        else:
            poster_url = None
            title = f"Фильм {movie_id}"
        film_player.url = trailer_url if trailer_url else "https://example.com/default.mp4"
        film_player.title = title
        film_player.state = "Stopped"
        film_player.current_time = 0
        await film_player.update_message()
        # Если найден постер, отправляем его в чат
        if poster_url:
            try:
                await client.send_file(chat, poster_url, caption=f"Постер: {title}")
            except Exception as e:
                print(f"Ошибка при отправке постера: {e}")
        await event.answer("Фильм выбран!")
    else:
        await event.answer("Неизвестная команда")

# Обработчик ввода текста от пользователя (для ввода ссылки или поискового запроса)
@client.on(events.NewMessage)
async def film_input_handler(event):
    chat = event.chat_id
    if chat in active_film_players:
        film_player = active_film_players[chat]
        # Если плеер ожидает прямой URL
        if film_player.state == "Awaiting URL" and not event.text.startswith('.'):
            url = event.text.strip()
            film_player.url = url
            film_player.title = url.split('/')[-1]
            film_player.state = "Stopped"
            film_player.current_time = 0
            await film_player.update_message()
            await event.delete()
        # Если плеер ожидает поискового запроса
        elif film_player.state == "Awaiting Search Query" and not event.text.startswith('.'):
            query = event.text.strip()
            results = search_movie_tmdb(query)
            if results:
                text = "🔍 **Результаты поиска:**\n"
                buttons = []
                for movie in results[:5]:
                    title = movie.get("title", "Без названия")
                    release_date = movie.get("release_date", "")[:4]
                    button_text = f"{title} ({release_date})"
                    buttons.append(Button.inline(button_text, f"film_select_{movie.get('id')}"))
                    text += f"- {button_text}\n"
                await event.reply(text, buttons=[buttons])
            else:
                await event.reply("❌ Фильмы не найдены по запросу.")
            film_player.state = "Stopped"
            await film_player.update_message()
            await event.delete()

@client.on(events.NewMessage(pattern=r"\.help"))
async def help_handler(event):
    """Показывает список доступных команд."""
    help_text = """🚀 **Доступные команды:**

`.ascii <текст>` - Преобразует текст в ASCII-арт
`.t <текст>` - Эффект печатающей машинки
`.cosmic <текст>` - Галактическая анимация
`/rundino` - Запуск игры "Бегущий динозавр"
`.cubbies` - Анимация "Cubbies Ripples"
`.heart` - Анимация сердца
`.wave <текст>` - Волнообразный эффект
`.merc <текст>` - Мерцание текста
`.spiral` - Анимация вращающейся спирали
`.wave_anim` - Анимация волны
`.fractal` - Анимация фрактала (треугольник Серпинского)
`.speak <текст>` - Озвучить текст (Android + Termux)
`.read` (ответ на сообщение) - Озвучить текст сообщения (Android + Termux)
`.foto_ascii` - Конвертация фото в ASCII-арт (ответьте на фото)
`.disable` - Отключить/включить анимации от других пользователей
`.film <название>` - Найти фильм по названию
`.help` - Показать это сообщение

✨ **Примеры использования:**
`.ascii Hello`
`.t Привет!`
`.cosmic Telegram`
`/rundino`
`.cubbies`
`.heart`
`.wave Привет`
`.merc Мерцание`
`.spiral`
`.wave_anim`
`.fractal`
`.speak Привет, мир!`
`.read` (ответ на сообщение)
`.foto_ascii` (ответьте на фото)
`.disable`
`.film Интерстеллар`
"""
    await event.reply(help_text)

@client.on(events.NewMessage(pattern=r"\.disable"))
async def disable_handler(event):
    """Отключает или включает анимации от других пользователей."""
    if event.sender_id != SELF_ID:
        return
    global DISABLE_ANIMATIONS
    DISABLE_ANIMATIONS = not DISABLE_ANIMATIONS
    # Сохраняем в конфиг
    phone, api_id, api_hash, _ = ConfigManager.load()
    ConfigManager.save(phone, api_id, api_hash, DISABLE_ANIMATIONS)
    state = "отключены" if DISABLE_ANIMATIONS else "включены"
    await event.reply(f"Анимации от других пользователей {state}.")

async def main():
    """Основная функция запуска бота."""
    await client.start(phone)
    self_user = await client.get_me()
    global SELF_ID
    SELF_ID = self_user.id
    print("🌠 Бот запущен!")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
