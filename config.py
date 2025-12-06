from dotenv import load_dotenv
import os

load_dotenv()

TELEGRAM_API_KEY = os.environ.get("TELEGRAM_API_KEY")
ADMIN_CHAT_ID = int(os.environ["ADMIN_CHAT_ID"]) if os.environ.get("ADMIN_CHAT_ID") else None
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
WEBHOOK_PATH = os.environ.get("WEBHOOK_PATH", "/telegram/webhook")
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "8000"))
