import io
import logging
import shutil
import zipfile
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import BackgroundTasks, FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
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
    help_command,
    makeup_recruiter_experience,
    model_recruiter_experience,
    next_steps,
    photographer_recruiter_experience,
    portfolio_requirements,
    privacy_rules,
    start,
    stylist_recruiter_experience,
)
from core.hendlers.callback import model_order
from core.utils.comands import set_commands


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if not config.TELEGRAM_API_KEY:
    raise RuntimeError("TELEGRAM_API_KEY must be set")


WEBHOOK_PATH = config.WEBHOOK_PATH if config.WEBHOOK_PATH.startswith("/") else f"/{config.WEBHOOK_PATH}"


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
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("portfolio", portfolio_requirements))
    application.add_handler(CommandHandler("next_steps", next_steps))

    application.add_handler(CallbackQueryHandler(model_order, pattern="^model_order_"))

    application.add_handler(MessageHandler(filters.PHOTO, get_photo))
    application.add_handler(MessageHandler(filters.VIDEO, get_video))


application = Application.builder().token(config.TELEGRAM_API_KEY).updater(None).build()
_register_handlers(application)


@asynccontextmanager
async def lifespan(app: FastAPI):  # pragma: no cover - startup/shutdown lifecycle
    webhook_url = _build_webhook_url()

    try:
        await application.initialize()
        await set_commands(application.bot)

        if webhook_url:
            try:
                await application.bot.set_webhook(webhook_url)
                logger.info("Webhook set to %s", webhook_url)
            except Exception as exc:  # pragma: no cover - defensive webhook setup
                logger.exception("Failed to set webhook: %s", exc)

        await application.start()

        if config.ADMIN_CHAT_ID:
            try:
                await application.bot.send_message(chat_id=config.ADMIN_CHAT_ID, text="Бот запущен")
            except Exception as exc:  # pragma: no cover - admin notification is optional
                logger.exception("Failed to notify admin on startup: %s", exc)
    except Exception as exc:  # pragma: no cover - keep service alive despite startup hiccups
        logger.exception("Startup sequence failed: %s", exc)

    try:
        yield
    finally:
        if config.ADMIN_CHAT_ID:
            try:
                await application.bot.send_message(chat_id=config.ADMIN_CHAT_ID, text="Бот отключен")
            except Exception as exc:  # pragma: no cover - admin notification is optional
                logger.exception("Failed to notify admin on shutdown: %s", exc)

        if application.bot and webhook_url:
            try:
                await application.bot.delete_webhook()
            except Exception as exc:  # pragma: no cover - defensive webhook cleanup
                logger.exception("Failed to delete webhook: %s", exc)

        try:
            await application.stop()
        except Exception as exc:  # pragma: no cover - defensive shutdown
            logger.exception("Failed to stop application cleanly: %s", exc)

        try:
            await application.shutdown()
        except Exception as exc:  # pragma: no cover - defensive shutdown
            logger.exception("Failed to shutdown application cleanly: %s", exc)


app = FastAPI(lifespan=lifespan)


@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
    except Exception as e:  # pragma: no cover - defensive logging
        logger.exception("Error processing Telegram update: %s", e)
        return {"ok": False}
    return {"ok": True}


@app.get("/")
async def healthcheck():
    return {"status": "ok"}


def _create_media_archive(buffer: io.BytesIO, media_dir: Path) -> int:
    files = [p for p in media_dir.rglob("*") if p.is_file()]

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for file_path in files:
            zip_file.write(file_path, file_path.relative_to(media_dir))

    return len(files)


@app.get("/media", response_class=HTMLResponse)
async def media_page():
    return """
    <html>
        <head><title>Media archive</title></head>
        <body>
            <h1>Download all uploaded media</h1>
            <p><a href=\"/media/download\">Download archive</a></p>
        </body>
    </html>
    """


@app.get("/media/download")
async def download_media(background_tasks: BackgroundTasks):
    media_dir = Path("media")
    if not media_dir.exists():
        return {"error": "No media available"}

    buffer = io.BytesIO()
    file_count = _create_media_archive(buffer, media_dir)

    if file_count == 0:
        return {"error": "No media files found"}

    buffer.seek(0)
    filename = f"media_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.zip"
    background_tasks.add_task(shutil.rmtree, media_dir, ignore_errors=True)

    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
        background=background_tasks,
    )

