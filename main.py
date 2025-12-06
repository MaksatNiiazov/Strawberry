import asyncio
import io
import logging
import shutil
import zipfile
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
from telegram import Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
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

    application.add_error_handler(error_handler)


application = Application.builder().token(config.TELEGRAM_API_KEY).build()
_polling_task: asyncio.Task | None = None
_shutdown_event: asyncio.Event | None = None


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors and notify admin/user without stopping the bot."""

    logger.exception("Unhandled exception during update processing", exc_info=context.error)

    admin_text = "Произошла ошибка в боте"
    if context.error:
        admin_text += f": {context.error}"

    if config.ADMIN_CHAT_ID:
        try:
            await context.bot.send_message(chat_id=config.ADMIN_CHAT_ID, text=admin_text)
        except Exception:  # pragma: no cover - best effort admin notification
            logger.debug("Failed to notify admin about an unhandled exception")

    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text("Произошла непредвиденная ошибка. Попробуйте позже.")
        except Exception:  # pragma: no cover - best effort user notification
            logger.debug("Failed to notify user about an unhandled exception")


_register_handlers(application)


async def _run_resilient_polling(restart_delay: float = 5.0) -> None:
    assert application.updater is not None

    while _shutdown_event and not _shutdown_event.is_set():
        try:
            await application.updater.start_polling(drop_pending_updates=True)
            logger.info("Bot polling started")

            if _shutdown_event:
                await _shutdown_event.wait()
        except Exception as exc:  # pragma: no cover - defensive restart
            logger.exception("Polling crashed; restarting in %.1f seconds: %s", restart_delay, exc)

            if _shutdown_event and _shutdown_event.is_set():
                break

            await asyncio.sleep(restart_delay)
        finally:
            if application.updater.running:
                try:
                    await application.updater.stop()
                except Exception as stop_exc:  # pragma: no cover - defensive stop
                    logger.exception("Failed to stop polling cleanly: %s", stop_exc)


@asynccontextmanager
async def lifespan(app: FastAPI):  # pragma: no cover - startup/shutdown lifecycle
    Path("media").mkdir(parents=True, exist_ok=True)
    global _polling_task, _shutdown_event

    try:
        await application.initialize()
        await set_commands(application.bot)

        try:
            await application.bot.delete_webhook(drop_pending_updates=True)
            logger.info("Existing webhooks removed; switching to polling mode")
        except Exception as exc:  # pragma: no cover - defensive webhook cleanup
            logger.exception("Failed to remove webhook before polling: %s", exc)

        await application.start()

        _shutdown_event = asyncio.Event()
        _polling_task = asyncio.create_task(_run_resilient_polling())

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
        if _shutdown_event:
            _shutdown_event.set()

        if _polling_task:
            try:
                await _polling_task
            except Exception as exc:  # pragma: no cover - defensive polling wait
                logger.exception("Polling task failed during shutdown: %s", exc)

        if config.ADMIN_CHAT_ID:
            try:
                await application.bot.send_message(chat_id=config.ADMIN_CHAT_ID, text="Бот отключен")
            except Exception as exc:  # pragma: no cover - admin notification is optional
                logger.exception("Failed to notify admin on shutdown: %s", exc)

        if application.updater:
            try:
                await application.updater.stop()
            except Exception as exc:  # pragma: no cover - defensive polling stop
                logger.exception("Failed to stop polling cleanly: %s", exc)

        try:
            await application.stop()
        except Exception as exc:  # pragma: no cover - defensive shutdown
            logger.exception("Failed to stop application cleanly: %s", exc)

        try:
            await application.shutdown()
        except Exception as exc:  # pragma: no cover - defensive shutdown
            logger.exception("Failed to shutdown application cleanly: %s", exc)


app = FastAPI(lifespan=lifespan)

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

