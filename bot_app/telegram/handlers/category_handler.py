# bot_app/telegram/handlers/category_handler.py
from bot_app.telegram.utils.api import send_telegram_message, delete_message, remove_reply_keyboard
from bot_app.telegram.state import user_context
from bot_app.telegram.constants import RETURN_TO_TYPING_BUTTON, BACK_TO_CATEGORIES_BUTTON
from bot_app.models import FAQCategory, FAQ, BotPage
import os

def _get_site_url():
    """Get the base site URL from settings for building mini-app links."""
    from django.conf import settings
    domain = getattr(settings, 'SITE_DOMAIN', None) or os.environ.get('SITE_DOMAIN', 'https://mytelebot.com')
    return domain.rstrip('/')

def send_categories_top(chat_id, bot):
    categories = FAQCategory.objects.filter(parent=None, bot=bot).order_by("name")
    if not categories.exists():
        send_telegram_message(chat_id, "No categories available.", reply_markup=remove_reply_keyboard())
        return

    keyboard = [[f"📂 {cat.name}"] for cat in categories]
    keyboard.append([RETURN_TO_TYPING_BUTTON])
    reply_markup = {"keyboard": keyboard, "resize_keyboard": True}
    
    send_telegram_message(chat_id, "👇 Choose a category:", reply_markup=reply_markup)

    user_context[chat_id] = {"level": "root", "category_id": None, "parent_id": None}

def send_category_content(chat_id, category, bot):
    loading_msg = send_telegram_message(chat_id, "⏳ Loading...", parse_mode="Markdown")

    subcategories = FAQCategory.objects.filter(parent=category, bot=bot).order_by("name")
    faqs = FAQ.objects.filter(category=category, bot=bot).order_by("question")
    pages = BotPage.objects.filter(category=category).order_by("created_at")

    user_context[chat_id] = {
        "level": "category",
        "category_id": category.id,
        "parent_id": category.parent.id if category.parent else None
    }

    keyboard = [[f"📂 {sub.name}"] for sub in subcategories]
    keyboard += [[f"❓ {q.question}"] for q in faqs]
    keyboard.append([BACK_TO_CATEGORIES_BUTTON])
    keyboard.append([RETURN_TO_TYPING_BUTTON])

    reply_markup = {"keyboard": keyboard, "resize_keyboard": True}

    has_content = subcategories.exists() or faqs.exists() or pages.exists()
    text = (
        f"📁 *{category.name}*\n 👇"
        if has_content
        else f"❌ No content found in {category.name}."
    )

    send_telegram_message(chat_id, text, reply_markup=reply_markup, parse_mode="Markdown")

    # Send pages as WebApp inline buttons (reply keyboard doesn't support web_app type)
    if pages.exists():
        base_url = _get_site_url()
        inline_buttons = []
        for page in pages:
            miniapp_url = f"{base_url}/dashboard/mini-app/page/{page.id}/"
            inline_buttons.append([{
                "text": f"📄 {page.name}",
                "web_app": {"url": miniapp_url}
            }])
        
        send_telegram_message(
            chat_id,
            "📋 *Pages:*",
            reply_markup={"inline_keyboard": inline_buttons},
            parse_mode="Markdown"
        )

    if loading_msg and "result" in loading_msg:
        delete_message(chat_id, loading_msg["result"]["message_id"])





def handle_back_button(chat_id, bot):
    context = user_context.get(chat_id)

    if not context or not context.get("category_id"):
        return send_categories_top(chat_id, bot)

    current_cat = FAQCategory.objects.filter(id=context["category_id"]).first()
    if not current_cat:
        return send_categories_top(chat_id, bot)

    parent_id = context.get("parent_id")
    if parent_id:
        parent_category = FAQCategory.objects.filter(id=parent_id).first()
        if parent_category:
            return send_category_content(chat_id, parent_category, bot)

    return send_categories_top(chat_id, bot)






# down here is the inline keyboard version
# bot_app/telegram/handlers/category_handler.py

# from bot_app.models import FAQCategory, FAQ
# from bot_app.telegram.utils.api import send_telegram_message
# from bot_app.telegram.handlers.faq_handler import send_faq_list
# from bot_app.telegram.utils.keyboards import build_category_inline_keyboard
# from bot_app.telegram.state import user_context


# def send_categories_top(chat_id):
#     """Send top-level categories"""
#     categories = FAQCategory.objects.filter(parent=None).order_by("name")
#     if not categories.exists():
#         send_telegram_message(chat_id, "No categories available.")
#         return

#     keyboard = build_category_replay_keyboard(categories, parent_id=None)
#     send_telegram_message(chat_id, "👋 Welcome! Choose a category:", reply_markup=keyboard)

#     # Save context
#     user_context[chat_id] = {"level": "root", "category_id": None, "parent_id": None}


# def send_category_content(chat_id, category):
#     """Show subcategories + list FAQ buttons via faq_handler"""
#     # Get subcategories and FAQs
#     subcategories = FAQCategory.objects.filter(parent=category).order_by("name")
#     faqs = FAQ.objects.filter(category=category).order_by("question")

#     # Send subcategories
#     if subcategories.exists():
#         keyboard = build_category_inline_keyboard(subcategories, parent_id=category.id)
#         send_telegram_message(chat_id, f"📁 *{category.name}*\nاختر قسمًا فرعيًا 👇",
#                               reply_markup=keyboard, parse_mode="Markdown")

#     # Send FAQ list via faq_handler
#     if faqs.exists():
#         send_faq_list(chat_id, faqs, parent_id=category.id)

#     # Save context
#     user_context[chat_id] = {
#         "level": "category",
#         "category_id": category.id,
#         "parent_id": category.parent.id if category.parent else None
#     }


# def handle_back_button(chat_id):
#     """Navigate back using saved context."""
#     context = user_context.get(chat_id)

#     if not context or not context.get("category_id"):
#         return send_categories_top(chat_id)

#     current_cat = FAQCategory.objects.filter(id=context["category_id"]).first()
#     if not current_cat:
#         return send_categories_top(chat_id)

#     parent_id = context.get("parent_id")
#     if parent_id:
#         parent_category = FAQCategory.objects.filter(id=parent_id).first()
#         if parent_category:
#             return send_category_content(chat_id, parent_category)

#     # Otherwise → top level
#     return send_categories_top(chat_id)
