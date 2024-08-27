from telegram import InlineKeyboardMarkup, InlineKeyboardButton

def model_experience():
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                text='Меня интересует только первый вариант',
                callback_data='model_order_default'
            )
        ],
        [
            InlineKeyboardButton(
                text='Я рассматриваю второй вариант',
                callback_data='model_order_webcam'
            )
        ]
    ])
    return keyboard
