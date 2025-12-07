import io
import logging
import shutil
import zipfile
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, Request
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


# ---------------------------------------------------------
# Logging
# ---------------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# ENV
# ---------------------------------------------------------

TELEGRAM_API_KEY = config.TELEGRAM_API_KEY
ADMIN_CHAT_ID = config.ADMIN_CHAT_ID

if not config.WEBHOOK_URL:
    raise RuntimeError("WEBHOOK_URL must be set to configure the Telegram webhook")

WEBHOOK_URL = config.WEBHOOK_URL.rstrip("/")      # https://example.onrender.com
WEBHOOK_PATH = config.WEBHOOK_PATH if config.WEBHOOK_PATH.startswith("/") else f"/{config.WEBHOOK_PATH}"
FULL_WEBHOOK_URL = f"{WEBHOOK_URL}{WEBHOOK_PATH}" # https://.../telegram/webhook

if not TELEGRAM_API_KEY:
    raise RuntimeError("TELEGRAM_API_KEY must be set")

logger.info(f"Webhook will be set to: {FULL_WEBHOOK_URL}")


# ---------------------------------------------------------
# Telegram Application
# ---------------------------------------------------------

application = Application.builder().token(TELEGRAM_API_KEY).build()


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception("Unhandled error occurred", exc_info=context.error)

    msg = "Произошла ошибка"
    if context.error:
        msg += f": {context.error}"

    if ADMIN_CHAT_ID:
        try:
            await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=msg)
        except Exception:
            pass

    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text("Произошла ошибка. Попробуйте позже.")
        except Exception:
            pass


def register_handlers(app: Application):
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


register_handlers(application)


# ---------------------------------------------------------
# Lifespan (startup + shutdown)
# ---------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):

    Path("media").mkdir(parents=True, exist_ok=True)

    await application.initialize()

    # set commands
    try:
        await set_commands(application.bot)
        logger.info("Bot commands set successfully")
    except Exception as e:
        logger.warning(f"Cannot set commands: {e}")

    # delete previous webhook and drop pending updates
    try:
        await application.bot.delete_webhook(drop_pending_updates=True)
    except Exception as e:
        logger.warning(f"Cannot delete webhook before setting a new one: {e}")

    # install new webhook
    await application.bot.set_webhook(
        FULL_WEBHOOK_URL,
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
    )
    logger.info(f"Webhook set: {FULL_WEBHOOK_URL}")

    await application.start()

    # notify admin
    if ADMIN_CHAT_ID:
        try:
            await application.bot.send_message(chat_id=ADMIN_CHAT_ID, text="Бот запущен (webhook mode)")
        except Exception:
            pass

    yield

    # remove webhook
    try:
        await application.bot.delete_webhook()
    except Exception:
        pass

    try:
        await application.stop()
    except Exception:
        pass

    try:
        await application.shutdown()
    except Exception:
        pass


# ---------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------

app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {
        "status": "ok",
        "mode": "webhook",
        "webhook": FULL_WEBHOOK_URL,
    }


# ---------------------------------------------------------
# Telegram Webhook Receiver
# ---------------------------------------------------------

@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.update_queue.put(update)
    return {"ok": True}


# ---------------------------------------------------------
# Media archive endpoints
# ---------------------------------------------------------

def _create_media_archive(buffer: io.BytesIO, media_dir: Path) -> int:
    files = [p for p in media_dir.rglob("*") if p.is_file()]

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as z:
        for file_path in files:
            z.write(file_path, file_path.relative_to(media_dir))

    return len(files)


@app.get("/media", response_class=HTMLResponse)
async def media_page():
    return """
    <html>
        <body>
            <h1>Download all media</h1>
            <p><a href='/media/download'>Download archive</a></p>
        </body>
    </html>
    """


@app.get("/media/download")
async def download_media(background_tasks: BackgroundTasks):
    media_dir = Path("media")

    if not media_dir.exists():
        return {"error": "No media available"}

    buffer = io.BytesIO()
    count = _create_media_archive(buffer, media_dir)

    if count == 0:
        return {"error": "No files found"}

    buffer.seek(0)
    filename = f"media_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.zip"

    background_tasks.add_task(shutil.rmtree, media_dir, ignore_errors=True)

    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


