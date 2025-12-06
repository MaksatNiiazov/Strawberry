from telegram import InlineKeyboardMarkup, InlineKeyboardButton

def model_experience():
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                text='Хочу работать в вебкам-формате',
                callback_data='model_order_webcam'
            )
        ]
    ])
    return keyboard
