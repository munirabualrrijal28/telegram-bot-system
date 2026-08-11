# bot_app/telegram/handlers/message_handler.py
from bot_app.telegram.utils.api import send_telegram_message, remove_reply_keyboard
from bot_app.telegram.handlers.category_handler import (
    send_categories_top,
    # handle_back_button,
    # send_subcategories_reply,
)
from bot_app.telegram.constants import (
    WELCOME_MESSAGES,
    BACK_TO_CATEGORIES_BUTTON,
    RETURN_TO_TYPING_BUTTON,
)




# bot_app/telegram/handlers/message_handler.py
from bot_app.telegram.utils.api import send_telegram_message, remove_reply_keyboard, delete_message
from bot_app.telegram.state import user_context
from bot_app.telegram.constants import WELCOME_MESSAGES, RETURN_TO_TYPING_BUTTON, BACK_TO_CATEGORIES_BUTTON
from bot_app.models import FAQCategory, FAQ
from bot_app.telegram.handlers.category_handler import send_categories_top, send_category_content, handle_back_button 

def handle_message(update):
    msg = update["message"]
    chat_id = msg["chat"]["id"]
    text = msg.get("text", "").strip()

    if text in WELCOME_MESSAGES or text == "/start":
        return send_categories_top(chat_id)

    if text == RETURN_TO_TYPING_BUTTON:
        send_telegram_message(chat_id, "✅ Returning to typing mode...", reply_markup=remove_reply_keyboard())
        return

    if text == BACK_TO_CATEGORIES_BUTTON:
        return handle_back_button(chat_id)

    # otherwise treat as subcategory or question
    return send_category_content(chat_id, text)


def handle_message_update(update, bot):
    msg = update["message"]
    chat_id = msg["chat"]["id"]
    text = msg.get("text", "").strip()

    # Parse start keywords from bot settings
    start_keywords = [k.strip().lower() for k in bot.start_keywords.split(",")] if bot.start_keywords else []
    # Add default /start if not present
    if "/start" not in start_keywords:
        start_keywords.append("/start")

    if text.lower() in start_keywords:
        # Send welcome message first if configured
        if bot.welcome_message:
            send_telegram_message(chat_id, bot.welcome_message)
        return send_categories_top(chat_id, bot)

    if text == RETURN_TO_TYPING_BUTTON:
        send_telegram_message(chat_id, "✅ Returning to typing mode...", reply_markup=remove_reply_keyboard())
        return

    if text == BACK_TO_CATEGORIES_BUTTON:
        handle_back_button(chat_id, bot)
        return

    # Selected a category
    category = FAQCategory.objects.filter(name__iexact=text.replace("📂 ", ""), bot=bot).first()
    if category:
        send_category_content(chat_id, category, bot)
        return

    # Selected a question
    faq = FAQ.objects.filter(question__iexact=text.replace("❓ ", ""), bot=bot).first()
    if faq:
        send_telegram_message(chat_id, f"💬 *{faq.question}*\n\n{faq.answer}", parse_mode="Markdown")
        return

    # Unknown input - use fallback message
    fallback = bot.fallback_message or "⚠️ Please choose a valid option."
    send_telegram_message(chat_id, fallback)


