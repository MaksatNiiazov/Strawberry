from telegram import BotCommand

def set_commands(bot):
    commands = [
        BotCommand("start", "Запустить бота"),
        BotCommand("about_platform", "О нашей платформе"),
        BotCommand("privacy_rules", "Правила Конфиденциальности")
    ]
    bot.set_my_commands(commands)
