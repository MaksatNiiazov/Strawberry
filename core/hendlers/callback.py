from telegram import Update
from telegram.ext import CallbackContext, CallbackQueryHandler

from core.texts.models.texts import MODEL_ORDER_WEBCAM, MODEL_ORDER_DEFAULT

def check_model_experience(update: Update, context: CallbackContext):
    call = update.callback_query
    experience = call.data.split('_')[-1]
    if experience == 'yes':
        answer = 'sssssssssss'
    elif experience == 'no':
        answer = 'awwwedasd'
    else:
        answer = 'awwwedasd'
    call.message.reply_text(answer)
    call.answer()

def model_order(update: Update, context: CallbackContext):
    call = update.callback_query
    experience = call.data.split('_')[-1]
    if experience == 'webcam':
        answer = MODEL_ORDER_WEBCAM
    elif experience == 'default':
        answer = MODEL_ORDER_DEFAULT
    else:
        answer = 'awwwedasd'

    call.message.reply_text(answer)
    call.answer()
