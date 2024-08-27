
from aiogram import Bot
from aiogram.types import CallbackQuery

from core.texts.models.texts import MODEL_ORDER_WEBCAM, MODEL_ORDER_DEFAULT


async def check_model_experience(call: CallbackQuery, bot: Bot):
    experience = call.data.split('_')[-1]
    if experience == 'yes':
        answer = 'sssssssssss'
    elif experience == 'no':
        answer = 'awwwedasd'
    else:
        answer = 'awwwedasd'
    await call.message.answer(answer)
    await call.answer()


async def model_order(call: CallbackQuery, bot: Bot):
    experience = call.data.split('_')[-1]
    if experience == 'webcam':
        answer = MODEL_ORDER_WEBCAM
    elif experience == 'default':
        answer = MODEL_ORDER_DEFAULT
    else:
        answer = 'awwwedasd'

    await call.message.answer(answer)
    await call.answer()
