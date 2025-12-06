from telegram import Update
from telegram.ext import ContextTypes

from core.texts.models.texts import MODEL_ORDER_DEFAULT, MODEL_ORDER_WEBCAM


async def check_model_experience(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    call = update.callback_query
    if not call:
        return

    experience = call.data.split("_")[-1]
    if experience == "yes":
        answer = "sssssssssss"
    elif experience == "no":
        answer = "awwwedasd"
    else:
        answer = "awwwedasd"

    if call.message:
        await call.message.reply_text(answer)

    await call.answer()


async def model_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    call = update.callback_query
    if not call:
        return

    experience = call.data.split("_")[-1]
    if experience == "webcam":
        answer = MODEL_ORDER_WEBCAM
    elif experience == "default":
        answer = MODEL_ORDER_DEFAULT
    else:
        answer = "awwwedasd"

    if call.message:
        await call.message.reply_text(answer)

    await call.answer()
