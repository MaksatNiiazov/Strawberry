import requests
import time
import config
import logging

# Импорт ваших функций
from core.hendlers.basic import start, get_photo, privacy_rules, get_video, model_recruiter_experience, about_platform, \
    photographer_recruiter_experience, stylist_recruiter_experience, makeup_recruiter_experience, equipment_help
from core.hendlers.callback import check_model_experience, model_order
from core.utils.comands import set_commands

# Логирование
logging.basicConfig(level=logging.INFO)

# Базовый URL для запросов к Telegram API
API_URL = f"https://api.telegram.org/bot{config.TELEGRAM_API_KEY}"


# Функция для отправки сообщений
def send_message(chat_id, text, parse_mode='HTML'):
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


# Обработчик команд и сообщений
def handle_updates(updates):
    for update in updates['result']:
        if 'message' in update:
            chat_id = update['message']['chat']['id']
            text = update['message'].get('text', '')

            if text.startswith('/'):
                handle_command(chat_id, text)
            elif 'photo' in update['message']:
                get_photo(chat_id, update['message']['photo'])
            elif 'video' in update['message']:
                get_video(chat_id, update['message']['video'])

        if 'callback_query' in update:
            callback_data = update['callback_query']['data']
            if callback_data.startswith('model_order_'):
                model_order(update['callback_query'])
            elif callback_data.startswith('model_experience_'):
                check_model_experience(update['callback_query'])


# Обработка команд
def handle_command(chat_id, text):
    if text == '/start':
        start(chat_id)
    elif text == '/model':
        model_recruiter_experience(chat_id)
    elif text == '/photographer':
        photographer_recruiter_experience(chat_id)
    elif text == '/makeup':
        makeup_recruiter_experience(chat_id)
    elif text == '/stylist':
        stylist_recruiter_experience(chat_id)
    elif text == '/about_platform':
        about_platform(chat_id)
    elif text == '/equipment':
        equipment_help(chat_id)
    elif text == '/privacy_rules':
        privacy_rules(chat_id)


# Функция для запуска бота
async def start_bot():
    # Установка команд
    set_commands()
    send_message(config.ADMIN_CHAT_ID, "Бот запущен")

    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if updates['ok'] and updates['result']:
            last_update_id = updates['result'][-1]['update_id']
            handle_updates(updates)
        time.sleep(1)


# Функция для остановки бота
async def stop_bot():
    send_message(config.ADMIN_CHAT_ID, "Бот отключен")


# Основной цикл
async def main():
    try:
        await start_bot()
    finally:
        await stop_bot()


# Запуск бота
if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
