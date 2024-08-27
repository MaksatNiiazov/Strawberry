from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command='start',
            description='Запустить бота'
        ),
        BotCommand(
            command='about_platform',
            description='О нашей платформе'
        ),
        BotCommand(
            command='privacy_rules',
            description='Правила Конфеденциальности'
        )
    ]
    await bot.set_my_commands(commands, BotCommandScopeDefault())