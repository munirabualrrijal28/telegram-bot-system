def build_category_inline_keyboard(categories, parent_id=None):
    keyboard = []
    for cat in categories:
        keyboard.append([{"text": cat.name, "callback_data": f"category_{cat.id}"}])

    # Always include a Back button (even for top-level)
    if parent_id:
        # Back to that parent category
        keyboard.append([{"text": "⬅️ Back", "callback_data": f"back_to_category_{parent_id}"}])
    else:
        # Back to start
        keyboard.append([{"text": "🏠 Home", "callback_data": "back_to_home"}])
        
    return {"inline_keyboard": keyboard}


def build_task_inline_keyboard(faqs, parent_id=None):
    keyboard = []
    for faq in faqs:
        keyboard.append([{"text": faq.question[:50], "callback_data": f"faq_{faq.id}"}])

    # Add Back button — go back to parent category or home
    if parent_id:
        keyboard.append([{"text": "⬅️ Back", "callback_data": f"back_to_category_{parent_id}"}])
    else:
        keyboard.append([{"text": "🏠 Home", "callback_data": "back_to_home"}])
    return {"inline_keyboard": keyboard}

def build_start_reply_keyboard():
    return {
        "keyboard": [[{"text": "🩺 Browse FAQs"}]],
        "resize_keyboard": True,
        "one_time_keyboard": True
    }



def remove_reply_keyboard():
    """Returns dict that removes the custom keyboard."""
    return {"remove_keyboard": True}



