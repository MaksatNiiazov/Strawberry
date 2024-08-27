import os
import logging
from datetime import datetime
from telegram import Update, Bot, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, CallbackQueryHandler, Filters

import config
from core.texts import basic
from core.keyboards.inlines import model_experience
from core.texts.models.texts import MODELING_TYPE_CHOICE, ABOUT_PLATFORM, MODEL_ORDER_DEFAULT, MODEL_ORDER_WEBCAM, \
    MODEL_EQUIPMENT
from core.texts.photographer.texts import PHOTOGRAPHER_ORDER_DEFAULT


def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text=basic.START_TEXT)


def get_photo(update: Update, context: CallbackContext):
    user_name = update.message.from_user.username
    folder_path = f'media/{user_name}/photos/'
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    largest_photo = update.message.photo[-1]
    file = context.bot.get_file(largest_photo.file_id)
    unique_file_name = datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3] + '.jpg'
    file.download(custom_path=f'{folder_path}/{unique_file_name}')
    context.bot.send_message(chat_id=config.ADMIN_CHAT_ID, text=f'{user_name}')
    update.message.reply_text(f'Photo added to {user_name} portfolio')


def get_video(update: Update, context: CallbackContext):
    user_name = update.message.from_user.username
    folder_path = f'media/{user_name}/videos/'
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    file = context.bot.get_file(update.message.video.file_id)
    unique_file_name = datetime.now().strftime('%Y%m%d%H%M%S') + '.mp4'
    file.download(custom_path=f'{folder_path}/{unique_file_name}')
    update.message.reply_text(f'Video added to {user_name} portfolio')


def model_recruiter_experience(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    reply_markup = model_experience()  # Вызов функции для получения клавиатуры
    update.message.reply_text(MODELING_TYPE_CHOICE, reply_markup=reply_markup)


def privacy_rules(update: Update, context: CallbackContext):
    update.message.reply_text(basic.CONFIDENTIALITY_POLICY)


def about_platform(update: Update, context: CallbackContext):
    update.message.reply_text(ABOUT_PLATFORM)


def photographer_recruiter_experience(update: Update, context: CallbackContext):
    update.message.reply_text(PHOTOGRAPHER_ORDER_DEFAULT)


def makeup_recruiter_experience(update: Update, context: CallbackContext):
    update.message.reply_text('В данный момент, к сожалению, нет открытых вакансий на позицию визажиста')


def stylist_recruiter_experience(update: Update, context: CallbackContext):
    update.message.reply_text('В данный момент, к сожалению, нет открытых вакансий на позицию стилиста')


def equipment_help(update: Update, context: CallbackContext):
    update.message.reply_text(MODEL_EQUIPMENT)


def main():
    API_TOKEN = config.TELEGRAM_API_KEY
    logging.basicConfig(level=logging.INFO)
    updater = Updater(token=API_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Регистрация обработчиков команд
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(MessageHandler(Filters.photo, get_photo))
    dp.add_handler(MessageHandler(Filters.video, get_video))
    dp.add_handler(CommandHandler('model', model_recruiter_experience))
    dp.add_handler(CommandHandler('privacy', privacy_rules))
    dp.add_handler(CommandHandler('about', about_platform))
    dp.add_handler(CommandHandler('photographer', photographer_recruiter_experience))
    dp.add_handler(CommandHandler('makeup', makeup_recruiter_experience))
    dp.add_handler(CommandHandler('stylist', stylist_recruiter_experience))
    dp.add_handler(CommandHandler('equipment', equipment_help))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
