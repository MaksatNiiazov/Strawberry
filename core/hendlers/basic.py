import logging
import os
from datetime import datetime
from typing import Optional

from telegram import Update
from telegram.ext import ContextTypes

import config
from core.keyboards.inlines import model_experience
from core.texts import basic
from core.texts.models.texts import (
    ABOUT_PLATFORM,
    MODELING_TYPE_CHOICE,
    MODEL_EQUIPMENT,
)
from core.texts.photographer.texts import PHOTOGRAPHER_ORDER_DEFAULT


logger = logging.getLogger(__name__)


def _user_folder(username: Optional[str], folder: str) -> str:
    safe_name = username or "anonymous"
    return os.path.join("media", safe_name, folder)


async def _forward_media_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not (config.ADMIN_CHAT_ID and update.effective_message):
        return

    try:
        forwarded_message = await context.bot.forward_message(
            chat_id=config.ADMIN_CHAT_ID,
            from_chat_id=update.effective_chat.id,
            message_id=update.effective_message.id,
        )
        logger.info("Forwarded message to admin: %s", forwarded_message)
    except Exception as exc:  # pragma: no cover - defensive admin forwarding
        logger.exception("Failed to forward media to admin: %s", exc)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_chat.send_message(text=basic.START_TEXT)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await update.message.reply_text(basic.HELP_TEXT)


async def get_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.photo:
        return

    try:
        await _forward_media_to_admin(update, context)

        user_name = update.message.from_user.username if update.message.from_user else "anonymous"
        folder_path = _user_folder(user_name, "photos")
        os.makedirs(folder_path, exist_ok=True)

        largest_photo = update.message.photo[-1]
        try:
            file = await context.bot.get_file(largest_photo.file_id)
            logger.info("FILE INFO: %s", file)
        except Exception as exc:
            logger.exception("Failed to retrieve photo file: %s", exc)
            raise
        unique_file_name = datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3] + ".jpg"
        await file.download_to_drive(custom_path=os.path.join(folder_path, unique_file_name))

        if config.ADMIN_CHAT_ID:
            await context.bot.send_message(chat_id=config.ADMIN_CHAT_ID, text=user_name)

        await update.message.reply_text(f"Photo added to {user_name} portfolio")
    except Exception as exc:  # pragma: no cover - defensive media handling
        logger.exception("Failed to process photo: %s", exc)
        if config.ADMIN_CHAT_ID:
            try:
                await context.bot.send_message(
                    chat_id=config.ADMIN_CHAT_ID,
                    text=f"Не удалось обработать фото пользователя: {exc}",
                )
            except Exception:  # pragma: no cover - best-effort notification
                logger.debug("Admin notification failed during photo error handling")

        if update.message:
            await update.message.reply_text("Произошла ошибка при обработке фото. Попробуйте позже.")


async def get_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.video:
        return

    try:
        await _forward_media_to_admin(update, context)

        user_name = update.message.from_user.username if update.message.from_user else "anonymous"
        folder_path = _user_folder(user_name, "videos")
        os.makedirs(folder_path, exist_ok=True)

        try:
            file = await context.bot.get_file(update.message.video.file_id)
            logger.info("FILE INFO: %s", file)
        except Exception as exc:
            logger.exception("Failed to retrieve video file: %s", exc)
            raise
        unique_file_name = datetime.now().strftime("%Y%m%d%H%M%S") + ".mp4"
        await file.download_to_drive(custom_path=os.path.join(folder_path, unique_file_name))

        await update.message.reply_text(f"Video added to {user_name} portfolio")
    except Exception as exc:  # pragma: no cover - defensive media handling
        logger.exception("Failed to process video: %s", exc)
        if config.ADMIN_CHAT_ID:
            try:
                await context.bot.send_message(
                    chat_id=config.ADMIN_CHAT_ID,
                    text=f"Не удалось обработать видео пользователя: {exc}",
                )
            except Exception:  # pragma: no cover - best-effort notification
                logger.debug("Admin notification failed during video error handling")

        if update.message:
            await update.message.reply_text("Произошла ошибка при обработке видео. Попробуйте позже.")


async def model_recruiter_experience(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    reply_markup = model_experience()
    await update.message.reply_text(MODELING_TYPE_CHOICE, reply_markup=reply_markup)


async def privacy_rules(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await update.message.reply_text(basic.CONFIDENTIALITY_POLICY)


async def about_platform(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await update.message.reply_text(ABOUT_PLATFORM)


async def portfolio_requirements(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await update.message.reply_text(basic.PORTFOLIO_REQUIREMENTS)


async def photographer_recruiter_experience(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await update.message.reply_text(PHOTOGRAPHER_ORDER_DEFAULT)


async def makeup_recruiter_experience(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await update.message.reply_text(
            "В данный момент, к сожалению, нет открытых вакансий на позицию визажиста"
        )


async def stylist_recruiter_experience(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await update.message.reply_text(
            "В данный момент, к сожалению, нет открытых вакансий на позицию стилиста"
        )


async def equipment_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await update.message.reply_text(MODEL_EQUIPMENT)


async def next_steps(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await update.message.reply_text(basic.NEXT_STEPS)
