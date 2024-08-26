import requests
import config

API_URL = f"https://api.telegram.org/bot{config.TELEGRAM_API_KEY}/setMyCommands"


def set_commands():
    commands = [
        {
            'command': 'start',
            'description': 'Запустить бота'
        },
        {
            'command': 'about_platform',
            'description': 'О нашей платформе'
        },
        {
            'command': 'privacy_rules',
            'description': 'Правила Конфиденциальности'
        }
    ]

    payload = {
        'commands': commands,
        'scope': {
            'type': 'default'
        }
    }

    response = requests.post(API_URL, json=payload)
    return response.json()
