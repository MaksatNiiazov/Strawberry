import logging
from telegram import Update, Bot, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, CallbackQueryHandler, Filters

import config
from core.hendlers.basic import start, get_photo, privacy_rules, get_video, model_recruiter_experience, about_platform, \
    photographer_recruiter_experience, stylist_recruiter_experience, makeup_recruiter_experience, equipment_help
from core.hendlers.callback import check_model_experience, model_order
from core.utils.comands import set_commands


def start_bot(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=config.ADMIN_CHAT_ID, text='Бот запущен')
    set_commands(context.bot)  # Установка команд для бота


def stop_bot(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=config.ADMIN_CHAT_ID, text='Бот отключен')


def main():
    API_TOKEN = config.TELEGRAM_API_KEY

    logging.basicConfig(level=logging.INFO)

    bot = Bot(API_TOKEN)
    updater = Updater(API_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Регистрация обработчиков команд
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('model', model_recruiter_experience))
    dispatcher.add_handler(CommandHandler('photographer', photographer_recruiter_experience))
    dispatcher.add_handler(CommandHandler('makeup', makeup_recruiter_experience))
    dispatcher.add_handler(CommandHandler('stylist', stylist_recruiter_experience))
    dispatcher.add_handler(CommandHandler('about_platform', about_platform))
    dispatcher.add_handler(CommandHandler('equipment', equipment_help))
    dispatcher.add_handler(CommandHandler('privacy_rules', privacy_rules))

    # Регистрация обработчиков для callback данных
    dispatcher.add_handler(CallbackQueryHandler(model_order, pattern='^model_order_'))
    dispatcher.add_handler(CallbackQueryHandler(check_model_experience, pattern='^model_experience_'))

    # Регистрация обработчиков для медиа
    dispatcher.add_handler(MessageHandler(Filters.photo, get_photo))
    dispatcher.add_handler(MessageHandler(Filters.video, get_video))

    # Начало и завершение работы
    dispatcher.add_handler(CommandHandler('start_bot', start_bot))
    dispatcher.add_handler(CommandHandler('stop_bot', stop_bot))

    # Запуск бота
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
