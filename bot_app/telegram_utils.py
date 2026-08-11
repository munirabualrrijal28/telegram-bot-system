# # bot_app/telegram_utils.py
# import json
# import html
# import requests
# from .models import BotSettings, FAQCategory, FAQ  # FAQ is your main FAQ model (not FAQQuestion)
# from django.conf import settings
# import time

# user_context = {}



# def get_bot_token():
#     bot = BotSettings.objects.filter(is_connected=True).first()
#     return bot.telegram_token if bot else None

# def _post_telegram(method, payload):
#     """Low-level POST helper - returns response JSON or None (and prints errors)."""
#     token = get_bot_token()
#     if not token:
#         print("telegram_utils: No connected bot (get_bot_token returned None).")
#         return None
#     url = f"https://api.telegram.org/bot{token}/{method}"
#     try:
#         r = requests.post(url, json=payload, timeout=10)
#         try:
#             r.raise_for_status()
#         except Exception as e:
#             print("telegram_utils: Telegram API returned error:", e)
#             print("telegram_utils: Response text:", getattr(r, "text", None))
#             return None
#         return r.json()
#     except Exception as e:
#         print("telegram_utils: Request failed:", e)
#         return None

# def send_telegram_message(chat_id, text, reply_markup=None, parse_mode="HTML"):
#     """Send a message. reply_markup should be Python dict (will be json.dumps)."""

#     # 


#     # 
#     safe_text = html.escape(text)
#     payload = {
#         "chat_id": chat_id,
#         "text": safe_text,
#         "parse_mode": parse_mode
#     }
#     if chat_id not in user_context:
#         user_context[chat_id] = {"level": "root", "category_id": None}

#     if reply_markup:
#         payload["reply_markup"] = json.dumps(reply_markup, ensure_ascii=False)
#     return _post_telegram("sendMessage", payload)

# def edit_message_text(chat_id, message_id, text, reply_markup=None, parse_mode="HTML"):
#     """
#     Edit an existing message's text + keyboard. Use when responding to callback_query
#     to replace the existing keyboard (Back behavior).
#     """
#     safe_text = html.escape(text)
#     payload = {
#         "chat_id": chat_id,
#         "message_id": message_id,
#         "text": safe_text,
#         "parse_mode": parse_mode
#     }
#     if reply_markup:
#         payload["reply_markup"] = json.dumps(reply_markup, ensure_ascii=False)
#     return _post_telegram("editMessageText", payload)

# # Inline keyboard builders (UUID safe)
# # def build_category_inline_keyboard(categories):
# #     keyboard = []
# #     for cat in categories:
# #         keyboard.append([{"text": cat.name, "callback_data": f"category_{cat.id}"}])
# #     return {"inline_keyboard": keyboard}

# # bot_app/telegram_utils.py
# def build_category_inline_keyboard(categories, parent_id=None):
#     keyboard = []
#     for cat in categories:
#         keyboard.append([{"text": cat.name, "callback_data": f"category_{cat.id}"}])

#     # Always include a Back button (even for top-level)
#     if parent_id:
#         # Back to that parent category
#         keyboard.append([{"text": "⬅️ Back", "callback_data": f"back_to_category_{parent_id}"}])
#     else:
#         # Back to start
#         keyboard.append([{"text": "🏠 Home", "callback_data": "back_to_home"}])
        
#     return {"inline_keyboard": keyboard}


# def build_task_inline_keyboard(faqs, parent_id=None):
#     keyboard = []
#     for faq in faqs:
#         keyboard.append([{"text": faq.question[:50], "callback_data": f"faq_{faq.id}"}])

#     # Add Back button — go back to parent category or home
#     if parent_id:
#         keyboard.append([{"text": "⬅️ Back", "callback_data": f"back_to_category_{parent_id}"}])
#     else:
#         keyboard.append([{"text": "🏠 Home", "callback_data": "back_to_home"}])
#     return {"inline_keyboard": keyboard}


# # def build_task_inline_keyboard(faqs):
# #     keyboard = []
# #     for faq in faqs:
# #         # Use faq.id (UUID) as callback_data: "faq_<uuid>"
# #         keyboard.append([{"text": (faq.question[:50] + ("…" if len(faq.question) > 50 else "")),
# #                           "callback_data": f"faq_{faq.id}"}])
# #     # Add Back button placeholder (callback_data "back_to_categories" or "back_to_category_<id>")
# #     keyboard.append([{"text": "⬅️ Back", "callback_data": "back_to_categories"}])
# #     return {"inline_keyboard": keyboard}

# def send_faq_answer(chat_id, faq):
#     text = f"Q: {faq.question}\n\nA: {faq.answer or 'No answer provided.'}"
#     # reply_markup: Back to categories
#     markup = {"inline_keyboard": [[{"text": "⬅️ Back", "callback_data": "back_to_categories"}]]}
#     return send_telegram_message(chat_id, text, reply_markup=markup)

# def build_start_reply_keyboard():
#     return {
#         "keyboard": [[{"text": "🩺 Browse FAQs"}]],
#         "resize_keyboard": True,
#         "one_time_keyboard": True
#     }



# # In telegram_utils.py, add this helper:
# def send_telegram_chat_action(chat_id, action="typing"):
#     payload = {"chat_id": chat_id, "action": action}
#     token = get_bot_token()
#     url = f"https://api.telegram.org/bot{token}/sendChatAction"
#     try:
#         requests.post(url, json=payload, timeout=5)
#     except Exception as e:
#         print("Error sending chat action:", e)
#         # 

# # for loading animated message
# def send_loading_message(chat_id, text="⏳ Loading…"):
#     """Send a temporary loading message."""
#     payload = {
#         "chat_id": chat_id,
#         "text": text
#     }
#     return _post_telegram("sendMessage", payload)

# def delete_message(chat_id, message_id):
#     """Delete a Telegram message."""
#     payload = {
#         "chat_id": chat_id,
#         "message_id": message_id
#     }
#     return _post_telegram("deleteMessage", payload)
# # 


# def remove_reply_keyboard():
#     """Returns dict that removes the custom keyboard."""
#     return {"remove_keyboard": True}

# #  dots waitng animation will not be used currently untll we add AI chatting feature
# def animate_loading(chat_id, base_text="⏳ Loading", cycles=3, delay=0.1):
#     """
#     Sends an animated loading message by editing it multiple times.
#     Returns the final message object (so you can delete it later).
#     """
#     # Send initial message
#     msg = send_telegram_message(chat_id, base_text)
#     if not msg or "result" not in msg:
#         return None
#     message_id = msg["result"]["message_id"]

#     # Animate dots: Loading. → Loading.. → Loading...
#     for i in range(cycles):
#         time.sleep(delay)
#         dots = "." * ((i % 3) + 1)
#         text = f"{base_text}{dots}"
#         _post_telegram("editMessageText", {
#             "chat_id": chat_id,
#             "message_id": message_id,
#             "text": text
#         })

#     return msg
