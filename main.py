import logging
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from telegram import Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

import config
from core.hendlers.basic import (
    about_platform,
    equipment_help,
    get_photo,
    get_video,
    makeup_recruiter_experience,
    model_recruiter_experience,
    photographer_recruiter_experience,
    privacy_rules,
    start,
    stylist_recruiter_experience,
)
from core.hendlers.callback import check_model_experience, model_order
from core.utils.comands import set_commands


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if not config.TELEGRAM_API_KEY:
    raise RuntimeError("TELEGRAM_API_KEY must be set")


WEBHOOK_PATH = config.WEBHOOK_PATH if config.WEBHOOK_PATH.startswith("/") else f"/{config.WEBHOOK_PATH}"
app = FastAPI()


def _build_webhook_url() -> Optional[str]:
    if not config.WEBHOOK_URL:
        logger.warning("WEBHOOK_URL is not set. Webhook will not be configured.")
        return None

    return f"{config.WEBHOOK_URL.rstrip('/')}{WEBHOOK_PATH}"


def _register_handlers(application: Application) -> None:
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("model", model_recruiter_experience))
    application.add_handler(CommandHandler("photographer", photographer_recruiter_experience))
    application.add_handler(CommandHandler("makeup", makeup_recruiter_experience))
    application.add_handler(CommandHandler("stylist", stylist_recruiter_experience))
    application.add_handler(CommandHandler("about_platform", about_platform))
    application.add_handler(CommandHandler("equipment", equipment_help))
    application.add_handler(CommandHandler("privacy_rules", privacy_rules))

    application.add_handler(CallbackQueryHandler(model_order, pattern="^model_order_"))
    application.add_handler(CallbackQueryHandler(check_model_experience, pattern="^model_experience_"))

    application.add_handler(MessageHandler(filters.PHOTO, get_photo))
    application.add_handler(MessageHandler(filters.VIDEO, get_video))


application = Application.builder().token(config.TELEGRAM_API_KEY).updater(None).build()
_register_handlers(application)


@app.on_event("startup")
async def on_startup() -> None:
    webhook_url = _build_webhook_url()

    await application.initialize()
    await set_commands(application.bot)

    if webhook_url:
        await application.bot.set_webhook(webhook_url)
        logger.info("Webhook set to %s", webhook_url)

    await application.start()

    if config.ADMIN_CHAT_ID:
        await application.bot.send_message(chat_id=config.ADMIN_CHAT_ID, text="Бот запущен")


@app.on_event("shutdown")
async def on_shutdown() -> None:
    if config.ADMIN_CHAT_ID:
        await application.bot.send_message(chat_id=config.ADMIN_CHAT_ID, text="Бот отключен")

    await application.bot.delete_webhook()
    await application.stop()
    await application.shutdown()


@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=400, detail="Invalid JSON") from exc

    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return {"ok": True}


@app.get("/")
async def healthcheck():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
    )
