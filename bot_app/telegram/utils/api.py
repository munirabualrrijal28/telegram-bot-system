
# def get_bot_token():
#     settings_obj = BotSettings.objects.filter(is_connected=True).first()
#     return settings_obj.telegram_token if settings_obj else None

# def telegram_request(method, data):
#     token = get_bot_token()
#     if not token:
#         return None
#     url = f"https://api.telegram.org/bot{token}/{method}"
#     try:
#         return requests.post(url, json=data).json()
#     except Exception:
#         return None

# def send_telegram_message(chat_id, text, reply_markup=None):
#     data = {"chat_id": chat_id, "text": text}
#     if reply_markup:
#         data["reply_markup"] = reply_markup
#     return telegram_request("sendMessage", data)

# def send_loading_message(chat_id, text="⏳ Loading…"):
#     return send_telegram_message(chat_id, text)

# def delete_message(chat_id, message_id):
#     return telegram_request("deleteMessage", {"chat_id": chat_id, "message_id": message_id})

# def remove_reply_keyboard():
#     return {"remove_keyboard": True}

# def animate_loading(chat_id, duration=3, interval=0.5):
#     """
#     Send an animated 'Loading...' message that updates a few times before deletion.
#     duration: total seconds to keep animating
#     interval: time between frames
#     """
#     frames = ["⏳ Loading", "⏳ Loading.", "⏳ Loading..", "⏳ Loading..."]
#     msg = send_telegram_message(chat_id, frames[0])
#     if not msg or "result" not in msg:
#         return None

#     message_id = msg["result"]["message_id"]

#     start_time = time.time()
#     while time.time() - start_time < duration:
#         for frame in frames:
#             telegram_request("editMessageText", {
#                 "chat_id": chat_id,
#                 "message_id": message_id,
#                 "text": frame
#             })
#             time.sleep(interval)
#             if time.time() - start_time >= duration:
#                 break

#     # Delete the loading message after finishing
#     delete_message(chat_id, message_id)
#     return True

# bot_app/telegram_utils.py
# bot_app/telegram/utils/api.py

import requests
from bot_app.models import BotSettings
import time
from bot_app.telegram.utils.keyboards import build_category_inline_keyboard, build_task_inline_keyboard ,remove_reply_keyboard
import json
import html
import requests
from bot_app.models import BotSettings, FAQCategory, FAQ  # FAQ is your main FAQ model (not FAQQuestion)
from django.conf import settings
import time

user_context = {}



def get_bot_token():
    bot = BotSettings.objects.filter(is_connected=True).first()
    return bot.telegram_token if bot else None

def _post_telegram(method, payload):
    """Low-level POST helper - returns response JSON or None (and prints errors)."""
    token = get_bot_token()
    if not token:
        print("telegram_utils: No connected bot (get_bot_token returned None).")
        return None
    url = f"https://api.telegram.org/bot{token}/{method}"
    try:
        r = requests.post(url, json=payload, timeout=10)
        try:
            r.raise_for_status()
        except Exception as e:
            print("telegram_utils: Telegram API returned error:", e)
            print("telegram_utils: Response text:", getattr(r, "text", None))
            return None
        return r.json()
    except Exception as e:
        print("telegram_utils: Request failed:", e)
        return None

def send_telegram_message(chat_id, text, reply_markup=None, parse_mode="HTML"):
    """Send a message. reply_markup should be Python dict (will be json.dumps)."""

    # 


    # 
    safe_text = html.escape(text)
    payload = {
        "chat_id": chat_id,
        "text": safe_text,
        "parse_mode": parse_mode
    }
    if chat_id not in user_context:
        user_context[chat_id] = {"level": "root", "category_id": None}

    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup, ensure_ascii=False)
    return _post_telegram("sendMessage", payload)

def edit_message_text(chat_id, message_id, text, reply_markup=None, parse_mode="HTML"):
    """
    Edit an existing message's text + keyboard. Use when responding to callback_query
    to replace the existing keyboard (Back behavior).
    """
    safe_text = html.escape(text)
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": safe_text,
        "parse_mode": parse_mode
    }
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup, ensure_ascii=False)
    return _post_telegram("editMessageText", payload)


# bot_app/telegram_utils.py



def send_faq_answer(chat_id, faq):
    text = f"Q: {faq.question}\n\nA: {faq.answer or 'No answer provided.'}"
    # reply_markup: Back to categories
    markup = {"inline_keyboard": [[{"text": "⬅️ Back", "callback_data": "back_to_categories"}]]}
    return send_telegram_message(chat_id, text, reply_markup=markup)


# In telegram_utils.py, add this helper:
def send_telegram_chat_action(chat_id, action="typing"):
    payload = {"chat_id": chat_id, "action": action}
    token = get_bot_token()
    url = f"https://api.telegram.org/bot{token}/sendChatAction"
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print("Error sending chat action:", e)
        # 

# for loading animated message
def send_loading_message(chat_id, text="⏳ Loading…"):
    """Send a temporary loading message."""
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    return _post_telegram("sendMessage", payload)

def delete_message(chat_id, message_id):
    """Delete a Telegram message."""
    payload = {
        "chat_id": chat_id,
        "message_id": message_id
    }
    return _post_telegram("deleteMessage", payload)
# 


#  dots waitng animation will not be used currently untll we add AI chatting feature
def animate_loading(chat_id, base_text="⏳ Loading", cycles=3, delay=0.1):
    """
    Sends an animated loading message by editing it multiple times.
    Returns the final message object (so you can delete it later).
    """
    # Send initial message
    msg = send_telegram_message(chat_id, base_text)
    if not msg or "result" not in msg:
        return None
    message_id = msg["result"]["message_id"]

    # Animate dots: Loading. → Loading.. → Loading...
    for i in range(cycles):
        time.sleep(delay)
        dots = "." * ((i % 3) + 1)
        text = f"{base_text}{dots}"
        _post_telegram("editMessageText", {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text
        })

    return msg
