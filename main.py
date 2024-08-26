import requests
import time
import config

# Функция для отправки сообщений
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{config.TELEGRAM_API_KEY}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    response = requests.post(url, json=data)
    print("Message sent: ", response.text)  # Для отладки

# Функция для установки команд бота
def set_commands():
    url = f"https://api.telegram.org/bot{config.TELEGRAM_API_KEY}/setMyCommands"
    commands = [
        {'command': 'start', 'description': 'Начать работу'},
        {'command': 'model', 'description': 'Информация для моделей'},
        {'command': 'photographer', 'description': 'Информация для фотографов'},
        {'command': 'makeup', 'description': 'Информация для визажистов'},
        {'command': 'stylist', 'description': 'Информация для стилистов'},
        {'command': 'about_platform', 'description': 'О платформе'},
        {'command': 'equipment', 'description': 'Помощь с оборудованием'},
        {'command': 'privacy_rules', 'description': 'Правила конфиденциальности'}
    ]
    response = requests.post(url, json={'commands': commands})
    print("Commands set: ", response.text)  # Для отладки

# Функция для получения обновлений от Telegram
def get_updates(last_update_id):
    url = f"https://api.telegram.org/bot{config.TELEGRAM_API_KEY}/getUpdates?timeout=100"
    if last_update_id:
        url += f"&offset={last_update_id + 1}"
    response = requests.get(url)
    return response.json()

# Обработка команд
def handle_updates(update):
    message = update['message']
    chat_id = message['chat']['id']
    text = message.get('text')

    if text == '/start':
        send_message(chat_id, "Привет! Я ваш бот.")
    elif text == '/model':
        send_message(chat_id, "Это информация для моделей.")
    # Добавьте другие команды по аналогии

# Основной цикл
def main():
    last_update_id = None
    set_commands()  # Установка команд на старте бота

    while True:
        updates = get_updates(last_update_id)
        if updates["ok"] and updates["result"]:
            for update in updates["result"]:
                last_update_id = update['update_id']
                handle_updates(update)
        time.sleep(1)

if __name__ == "__main__":
    main()
