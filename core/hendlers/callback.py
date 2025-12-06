from telegram import Update
from telegram.ext import ContextTypes

from core.texts.models.texts import MODEL_ORDER_WEBCAM


async def model_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    call = update.callback_query
    if not call:
        return

    experience = call.data.split("_")[-1]
    if experience == "webcam":
        answer = MODEL_ORDER_WEBCAM
    else:
        answer = "Мы работаем только в вебкам-формате. Нажмите кнопку, чтобы получить инструкцию по портфолио."

    if call.message:
        await call.message.reply_text(answer)

    await call.answer()
