import requests

def handle_callback(update, bot):
    """
    Handle inline button callbacks.
    For now, we just acknowledge the callback to stop the loading animation.
    Future: Parse callback_data (e.g., "cat:123") and trigger logic.
    """
    try:
        callback_query = update.get("callback_query", {})
        callback_id = callback_query.get("id")
        # chat_id = callback_query.get("message", {}).get("chat", {}).get("id")
        # data = callback_query.get("data")

        if callback_id:
            # Acknowledge callback to stop loading state on client
            url = f"https://api.telegram.org/bot{bot.telegram_token}/answerCallbackQuery"
            payload = {
                "callback_query_id": callback_id,
                "text": "Selected!"  # Optional toast message
            }
            requests.post(url, json=payload)
            
            # TODO: Add specific logic based on 'data'
            # e.g., if data.startswith("cat:"): show_category(chat_id, data.split(":")[1])
            
    except Exception as e:
        print(f"Error handling callback: {e}")

