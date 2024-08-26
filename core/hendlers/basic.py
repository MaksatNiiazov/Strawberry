import requests
import os
from datetime import datetime
import asyncio
import config

from core.texts import basic
from core.keyboards.inlines import model_experience
from core.texts.models.texts import MODELING_TYPE_CHOICE, ABOUT_PLATFORM, MODEL_ORDER_DEFAULT, MODEL_ORDER_WEBCAM, \
    MODEL_EQUIPMENT
from core.texts.photographer.texts import PHOTOGRAPHER_ORDER_DEFAULT

API_URL = f"https://api.telegram.org/bot{config.TELEGRAM_API_KEY}/"


# Функция для отправки сообщения
async def send_message(chat_id, text, parse_mode='HTML'):
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': parse_mode
    }
    response = requests.post(f"{API_URL}sendMessage", json=payload)
    return response.json()


# Стартовая команда
async def start(chat_id):
    await send_message(chat_id, basic.START_TEXT)


# Обработчик фотографий
async def get_photo(message, bot_token):
    user_name = message['from']['username']  # Получаем имя пользователя
    chat_id = message['chat']['id']
    folder_path = 'media/'
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    folder_path += f'{user_name}/photos/'
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    largest_photo = message['photo'][-1]

    # Получение файла
    file_id = largest_photo['file_id']
    get_file_url = f"{API_URL}getFile?file_id={file_id}"
    file_info = requests.get(get_file_url).json()

    # Скачиваем файл
    file_path = file_info['result']['file_path']
    download_url = f"https://api.telegram.org/file/bot{bot_token}/{file_path}"
    unique_file_name = datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3] + '.jpg'

    with open(f'{folder_path}/{unique_file_name}', 'wb') as file:
        file.write(requests.get(download_url).content)

    await asyncio.sleep(0.001)  # Добавляем задержку для уникальности имен файлов
    await send_message(config.ADMIN_CHAT_ID, f'{user_name}')  # Уведомляем админа
    await send_message(chat_id, f'Photo added to {user_name} portfolio')  # Сообщаем пользователю


# Обработчик видео
async def get_video(message, bot_token):
    user_name = message['from']['username']
    chat_id = message['chat']['id']
    folder_path = f'media/{user_name}/videos/'
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    await send_message(chat_id, f'Video added to {user_name} portfolio')

    file_id = message['video']['file_id']
    get_file_url = f"{API_URL}getFile?file_id={file_id}"
    file_info = requests.get(get_file_url).json()

    file_path = file_info['result']['file_path']
    download_url = f"https://api.telegram.org/file/bot{bot_token}/{file_path}"
    unique_file_name = datetime.now().strftime('%Y%m%d%H%M%S') + '.mp4'

    with open(f'{folder_path}/{unique_file_name}', 'wb') as file:
        file.write(requests.get(download_url).content)


### MODEL ###

# Опыт моделей
async def model_recruiter_experience(chat_id):
    await send_message(chat_id, MODELING_TYPE_CHOICE, parse_mode=None)


# Правила конфиденциальности
async def privacy_rules(chat_id):
    await send_message(chat_id, basic.CONFIDENTIALITY_POLICY)


# О платформе
async def about_platform(chat_id):
    await send_message(chat_id, ABOUT_PLATFORM)


### MODEL_END ###

### PHOTOGRAPHER ###

# Опыт фотографа
async def photographer_recruiter_experience(chat_id):
    await send_message(chat_id, PHOTOGRAPHER_ORDER_DEFAULT)


### PHOTOGRAPHER_END ###

# Опыт визажиста
async def makeup_recruiter_experience(chat_id):
    await send_message(chat_id, 'В данный момент, к сожалению, нет открытых вакансий на позицию визажиста')


# Опыт стилиста
async def stylist_recruiter_experience(chat_id):
    await send_message(chat_id, 'В данный момент, к сожалению, нет открытых вакансий на позицию стилиста')


# Помощь с оборудованием
async def equipment_help(chat_id):
    await send_message(chat_id, MODEL_EQUIPMENT)
