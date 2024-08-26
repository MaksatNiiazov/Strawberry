import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command

import config
from core.hendlers.basic import start, get_photo, privacy_rules, get_video, model_recruiter_experience, about_platform,\
    photographer_recruiter_experience, stylist_recruiter_experience, makeup_recruiter_experience, equipment_help
from core.hendlers.callback import check_model_experience, model_order
from core.utils.comands import set_commands

async def start_bot(dispatcher):
    bot = dispatcher.bot
    await set_commands(bot)
    await bot.send_message(config.ADMIN_CHAT_ID, text='Бот запущен')

async def stop_bot(dispatcher):
    bot = dispatcher.bot
    await bot.send_message(config.ADMIN_CHAT_ID, text='Бот отключен')

async def main():
    API_TOKEN = config.TELEGRAM_API_KEY

    logging.basicConfig(level=logging.INFO)

    # Initialize Bot and Dispatcher
    bot = Bot(token=API_TOKEN, parse_mode='HTML')
    dp = Dispatcher()

    # Registering handlers
    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)

    dp.message.register(start, Command(commands=['start']))
    dp.message.register(model_recruiter_experience, Command(commands=['model']))
    dp.message.register(photographer_recruiter_experience, Command(commands=['photographer']))
    dp.message.register(makeup_recruiter_experience, Command(commands=['makeup']))
    dp.message.register(stylist_recruiter_experience, Command(commands=['stylist']))
    dp.message.register(about_platform, Command(commands=['about_platform']))
    dp.message.register(equipment_help, Command(commands=['equipment']))

    dp.callback_query.register(model_order, F.data.startswith('model_order_'))
    dp.callback_query.register(check_model_experience, F.data.startswith('model_experience_'))

    dp.message.register(get_photo, F.photo)
    dp.message.register(get_video, F.video)
    dp.message.register(privacy_rules, Command(commands=['privacy_rules']))

    try:
        # Start polling
        await dp.start_polling()
    finally:
        # Close the session
        await dp.storage.close()
        await dp.bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
