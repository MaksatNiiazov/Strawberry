import asyncio
import os
from datetime import datetime

from aiogram import types, Bot, F

import config
from core.texts import basic
from core.keyboards.inlines import model_experience
from core.texts.models.texts import MODELING_TYPE_CHOICE, ABOUT_PLATFORM, MODEL_ORDER_DEFAULT, MODEL_ORDER_WEBCAM, \
    MODEL_EQUIPMENT
from core.texts.photographer.texts import PHOTOGRAPHER_ORDER_DEFAULT


async def start(message: types.Message):
    await message.answer(basic.START_TEXT)


async def get_photo(message: types.Message, bot: Bot):
    user_name = message.from_user.username  # Получаем имя пользователя
    folder_path = 'media/'
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    # folder_path += f'{type}/'
    # if not os.path.exists(folder_path):
    #     os.makedirs(folder_path)
    folder_path += f'{user_name}/'
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    folder_path += f'photos'


    # Проверяем, существует ли папка, и создаем ее, если необходимо
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Выбираем фото с наибольшим разрешением
    largest_photo = message.photo[-1]

    file = await bot.get_file(largest_photo.file_id)
    unique_file_name = datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3] + '.jpg'
    await bot.download_file(file.file_path, f'{folder_path}/{unique_file_name}')

    # Добавляем небольшую задержку, чтобы имена файлов были уникальными
    await asyncio.sleep(0.001)
    await bot.send_message(config.ADMIN_CHAT_ID, text=f'{user_name}')
    await message.answer(f'Photo added to {user_name} portfolio') 

async def get_video(message: types.Message, bot: Bot):
    user_name = message.from_user.username  # Получаем имя пользователя
    folder_path = f'media/{user_name}/videos/'  # Создаем путь к папке с именем пользователя
    if not os.path.exists(folder_path):  # Проверяем, существует ли папка
        os.makedirs(folder_path)  # Создаем папку, если она не существует
    await message.answer(f'Video added to {user_name} portfolio')  # Отправляем сообщение с именем пользователя

    if not os.path.exists(folder_path):  # Проверяем, существует ли папка
        os.makedirs(folder_path)  # Создаем папку, если она не существует

    # Обрабатываем видеофайл
    file = await bot.get_file(message.video.file_id)
    unique_file_name = datetime.now().strftime('%Y%m%d%H%M%S') + '.mp4'
    await bot.download_file(file.file_path, f'{folder_path}/{unique_file_name}')  # Сохраняем видео с уникальным именем


### MODEL ###

async def model_recruiter_experience(message: types.Message, bot: Bot):
    await message.answer(MODELING_TYPE_CHOICE, reply_markup=model_experience)


async def privacy_rules(message: types.Message):
    await message.answer(basic.CONFIDENTIALITY_POLICY)


async def about_platform(message: types.Message):
    await message.answer(ABOUT_PLATFORM)


### MODEL_END ###

### PHOTOGRAPHER ###

async def photographer_recruiter_experience(message: types.Message):
    await message.answer(PHOTOGRAPHER_ORDER_DEFAULT)

### PHOTOGRAPHER_END ###


async def makeup_recruiter_experience(message: types.Message):
    await message.answer('В данный момент, к сожалению, нет открытых вакансий на позицию визажиста')


async def stylist_recruiter_experience(message: types.Message):
    await message.answer('В данный момент, к сожалению, нет открытых вакансий на позицию стилиста')


async def equipment_help(message: types.Message):
    await message.answer(MODEL_EQUIPMENT)
