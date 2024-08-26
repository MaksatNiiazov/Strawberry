import requests
import time
import asyncio
import logging
import config

from core.hendlers.basic import start, get_photo, privacy_rules, get_video, model_recruiter_experience, about_platform, \
    photographer_recruiter_experience, stylist_recruiter_experience, makeup_recruiter_experience, equipment_help
from core.hendlers.callback import check_model_experience, model_order
from core.utils.comands import set_commands

# Логирование
logging.basicConfig(level=logging.INFO)

# Базовый URL для запросов к Telegram API
API_URL = f"https://api.telegram.org/bot{config.TELEGRAM_API_KEY}"


# Функция для отправки сообщений
async def send_message(chat_id, text, parse_mode='HTML'):
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': parse_mode
    }
    response = requests.post(f"{API_URL}/sendMessage", json=payload)
    return response.json()


# Функция для получения обновлений
def get_updates(offset=None):
    params = {'timeout': 100}
    if offset:
        params['offset'] = offset + 1
    response = requests.get(f"{API_URL}/getUpdates", params=params)
    return response.json()


# Моделируем объект Bot для передачи в set_commands
class Bot:
    def __init__(self, token):
        self.token = token
        self.api_url = f"https://api.telegram.org/bot{token}"

    async def send_message(self, chat_id, text, parse_mode='HTML'):
        payload = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode
        }
        return requests.post(f"{self.api_url}/sendMessage", json=payload).json()


# Обработчик команд и сообщений
async def handle_updates(updates, bot):
    for update in updates['result']:
        if 'message' in update:
            chat_id = update['message']['chat']['id']
            text = update['message'].get('text', '')

            if text.startswith('/'):
                await handle_command(chat_id, text, bot)
            elif 'photo' in update['message']:
                await get_photo(chat_id, update['message']['photo'])
            elif 'video' in update['message']:
                await get_video(chat_id, update['message']['video'])

        if 'callback_query' in update:
            callback_data = update['callback_query']['data']
            if callback_data.startswith('model_order_'):
                await model_order(update['callback_query'])
            elif callback_data.startswith('model_experience_'):
                await check_model_experience(update['callback_query'])


# Обработка команд
async def handle_command(chat_id, text, bot):
    if text == '/start':
        await start(chat_id)
    elif text == '/model':
        await model_recruiter_experience(chat_id)
    elif text == '/photographer':
        await photographer_recruiter_experience(chat_id)
    elif text == '/makeup':
        await makeup_recruiter_experience(chat_id)
    elif text == '/stylist':
        await stylist_recruiter_experience(chat_id)
    elif text == '/about_platform':
        await about_platform(chat_id)
    elif text == '/equipment':
        await equipment_help(chat_id)
    elif text == '/privacy_rules':
        await privacy_rules(chat_id)


# Функция для запуска бота
async def start_bot():
    bot = Bot(config.TELEGRAM_API_KEY)  # Создаем объект Bot
    await set_commands(bot)  # Передаем объект bot в set_commands

    await send_message(config.ADMIN_CHAT_ID, "Бот запущен")

    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if updates['ok'] and updates['result']:
            last_update_id = updates['result'][-1]['update_id']
            await handle_updates(updates, bot)
        time.sleep(1)


# Функция для остановки бота
async def stop_bot():
    await send_message(config.ADMIN_CHAT_ID, "Бот отключен")


# Основной цикл
async def main():
    try:
        await start_bot()
    finally:
        await stop_bot()


# Запуск бота
if __name__ == "__main__":
    asyncio.run(main())
