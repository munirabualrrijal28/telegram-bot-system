# bot_app/telegram/utils/loader.py
import os
from django.conf import settings

BOT_TOKEN = getattr(settings, "TELEGRAM_BOT_TOKEN", os.getenv("TELEGRAM_BOT_TOKEN"))
BOT_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
