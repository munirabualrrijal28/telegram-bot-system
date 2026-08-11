# bot_app/telegram/handlers/faq_handler.py
from bot_app.models import FAQ
from bot_app.telegram.utils.api import send_telegram_message, remove_reply_keyboard
from bot_app.telegram.utils.keyboards import build_task_inline_keyboard

def send_faq_list(chat_id, faqs, parent_id=None):
    """Send a list of FAQs as inline keyboard"""
    if not faqs:
        send_telegram_message(chat_id, "❌ No questions available.", reply_markup=remove_reply_keyboard())
        return

    keyboard = build_task_inline_keyboard(faqs, parent_id=parent_id)
    send_telegram_message(chat_id, "❓ اختر سؤالاً:", reply_markup=keyboard)


def send_faq_answer(chat_id, faq):
    """Send an individual FAQ answer with a Back button"""
    text = f"💬 *{faq.question}*\n\n{faq.answer or 'No answer provided.'}"
    markup = {"inline_keyboard": [[{"text": "⬅️ Back", "callback_data": "back_to_categories"}]]}
    send_telegram_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")
