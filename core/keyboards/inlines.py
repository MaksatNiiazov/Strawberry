from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

model_experience = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Меня интересует только первый вариант',
                callback_data='model_order_default'
            ),
        ],
        [
            InlineKeyboardButton(
                text='Я рассматриваю второй вариант',
                callback_data='model_order_webcam'
            ),
        ]
    ])
