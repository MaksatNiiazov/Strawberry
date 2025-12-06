from telegram import Bot, BotCommand


async def set_commands(bot: Bot) -> None:
    commands = [
        BotCommand("start", "Запустить бота"),
        BotCommand("help", "Как пользоваться ботом"),
        BotCommand("model", "Варианты работы для моделей"),
        BotCommand("about_platform", "О нашей платформе"),
        BotCommand("portfolio", "Требования к портфолио"),
        BotCommand("next_steps", "Что произойдет после заявки"),
        BotCommand("equipment", "Что входит в поддержку оборудованием"),
        BotCommand("privacy_rules", "Правила Конфиденциальности"),
    ]
    await bot.set_my_commands(commands)
