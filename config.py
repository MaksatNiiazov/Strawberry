from dotenv import load_dotenv
import os

load_dotenv()

TELEGRAM_API_KEY = os.environ.get('TELEGRAM_API_KEY')
ADMIN_CHAT_ID = os.environ.get('ADMIN_CHAT_ID')