from telegram import Bot, BotCommand


async def set_commands(bot: Bot) -> None:
    commands = [
        BotCommand("start", "Запустить бота"),
        BotCommand("about_platform", "О нашей платформе"),
        BotCommand("privacy_rules", "Правила Конфиденциальности"),
    ]
    await bot.set_my_commands(commands)
