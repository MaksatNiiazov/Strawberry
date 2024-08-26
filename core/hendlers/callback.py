import requests
import config
from core.texts.models.texts import MODEL_ORDER_WEBCAM, MODEL_ORDER_DEFAULT

API_URL = f"https://api.telegram.org/bot{config.TELEGRAM_API_KEY}/"


# Функция для отправки сообщений через Telegram API
async def send_message(chat_id, text, parse_mode='HTML'):
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': parse_mode
    }
    response = requests.post(f"{API_URL}sendMessage", json=payload)
    return response.json()


# Функция для отправки ответа на коллбек-запрос через Telegram API
async def answer_callback_query(callback_query_id, text=None):
    payload = {
        'callback_query_id': callback_query_id,
        'text': text if text else ''
    }
    response = requests.post(f"{API_URL}answerCallbackQuery", json=payload)
    return response.json()


# Проверка опыта модели
async def check_model_experience(callback_data, chat_id, callback_query_id):
    experience = callback_data.split('_')[-1]

    if experience == 'yes':
        answer = 'sssssssssss'
    elif experience == 'no':
        answer = 'awwwedasd'
    else:
        answer = 'awwwedasd'

    await send_message(chat_id, answer)
    await answer_callback_query(callback_query_id)


# Заказ модели
async def model_order(callback_data, chat_id, callback_query_id):
    experience = callback_data.split('_')[-1]

    if experience == 'webcam':
        answer = MODEL_ORDER_WEBCAM
    elif experience == 'default':
        answer = MODEL_ORDER_DEFAULT
    else:
        answer = 'awwwedasd'

    await send_message(chat_id, answer)
    await answer_callback_query(callback_query_id)
