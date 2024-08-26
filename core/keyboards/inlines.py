import json


# Функция для создания инлайн-клавиатуры
def create_model_experience_keyboard():
    inline_keyboard = [
        [
            {
                'text': 'Меня интересует только первый вариант',
                'callback_data': 'model_order_default'
            },
        ],
        [
            {
                'text': 'Я рассматриваю второй вариант',
                'callback_data': 'model_order_webcam'
            },
        ]
    ]
    return json.dumps({'inline_keyboard': inline_keyboard})


# Пример использования клавиатуры в сообщении
async def send_model_experience(chat_id):
    # Создаем инлайн-клавиатуру
    reply_markup = create_model_experience_keyboard()

    # Отправляем сообщение с инлайн-клавиатурой
    payload = {
        'chat_id': chat_id,
        'text': 'Выберите вариант:',
        'reply_markup': reply_markup
    }
    response = requests.post(f"{API_URL}sendMessage", json=payload)
    return response.json()
