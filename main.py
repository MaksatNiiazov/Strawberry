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


# ============================================================
#   APPLICATION
# ============================================================

application = Application.builder().token(config.TELEGRAM_API_KEY).build()


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception("Unhandled error", exc_info=context.error)

    msg = "Произошла ошибка"
    if context.error:
        msg += f": {context.error}"

    # уведомляем админа
    if config.ADMIN_CHAT_ID:
        try:
            await context.bot.send_message(chat_id=config.ADMIN_CHAT_ID, text=msg)
        except Exception:
            pass

    # уведомляем пользователя
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text("Произошла непредвиденная ошибка. Попробуйте позже.")
        except Exception:
            pass


# Регистрация хендлеров
def _register_handlers(app: Application) -> None:
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("model", model_recruiter_experience))
    app.add_handler(CommandHandler("photographer", photographer_recruiter_experience))
    app.add_handler(CommandHandler("makeup", makeup_recruiter_experience))
    app.add_handler(CommandHandler("stylist", stylist_recruiter_experience))
    app.add_handler(CommandHandler("about_platform", about_platform))
    app.add_handler(CommandHandler("equipment", equipment_help))
    app.add_handler(CommandHandler("privacy_rules", privacy_rules))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("portfolio", portfolio_requirements))
    app.add_handler(CommandHandler("next_steps", next_steps))

    app.add_handler(CallbackQueryHandler(model_order, pattern="^model_order_"))

    app.add_handler(MessageHandler(filters.PHOTO, get_photo))
    app.add_handler(MessageHandler(filters.VIDEO, get_video))

    app.add_error_handler(error_handler)


_register_handlers(application)


# ============================================================
#   POLLING LOOP (без Updater!)
# ============================================================

_shutdown_event: asyncio.Event | None = None
_polling_task: asyncio.Task | None = None


async def _polling_loop() -> None:
    """
    Чистый polling, полностью совместимый с Python 3.13.
    Не использует Updater.
    Работает бесконечно, перезапускаясь при ошибках.
    """
    while not _shutdown_event.is_set():
        try:
            await application.initialize()
            await set_commands(application.bot)

            # удаляем webhook, чтобы Render не завис
            try:
                await application.bot.delete_webhook(drop_pending_updates=True)
            except Exception:
                logger.warning("Failed to delete webhook before polling")

            logger.info("Starting polling…")
            await application.run_polling(
                allowed_updates=Update.ALL_TYPES,
                stop_signals=None,   # важно для serverless
            )

        except Exception as exc:
            logger.exception("Polling crashed: %s", exc)
            await asyncio.sleep(5)


# ============================================================
#   FASTAPI LIFESPAN
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _shutdown_event, _polling_task

    Path("media").mkdir(parents=True, exist_ok=True)

    _shutdown_event = asyncio.Event()
    _polling_task = asyncio.create_task(_polling_loop())

    # уведомление админа о старте
    if config.ADMIN_CHAT_ID:
        try:
            await application.bot.send_message(chat_id=config.ADMIN_CHAT_ID, text="Бот запущен")
        except Exception:
            pass

    yield

    # SHUTDOWN
    _shutdown_event.set()
    await asyncio.sleep(0.1)

    if _polling_task:
        try:
            await _polling_task
        except Exception:
            pass

    # уведомление админа об остановке
    if config.ADMIN_CHAT_ID:
        try:
            await application.bot.send_message(chat_id=config.ADMIN_CHAT_ID, text="Бот остановлен")
        except Exception:
            pass

    try:
        await application.shutdown()
    except Exception:
        pass


app = FastAPI(lifespan=lifespan)


# ============================================================
#   API ROUTES
# ============================================================

@app.get("/")
async def healthcheck():
    return {"status": "ok"}


def _create_media_archive(buffer: io.BytesIO, media_dir: Path) -> int:
    files = [p for p in media_dir.rglob("*") if p.is_file()]

    with zipfile.ZipFile(buffer, "w", zipfile.ZZIP_DEFLATED) as zip_file:
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
            <p><a href="/media/download">Download archive</a></p>
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
