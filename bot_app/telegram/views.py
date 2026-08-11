# bot_app/telegram/views.py
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from bot_app.telegram.handlers.message_handler import handle_message_update
from bot_app.telegram.handlers.callback_handler import handle_callback  # Enabled!

@csrf_exempt
def telegram_webhook(request, token):
    print(f"🔹 Webhook received! Token: {token}")
    print(f"🔹 Method: {request.method}")
    
    if request.method != "POST":
        return JsonResponse({"status": "ok"})

    try:
        print(f"🔹 Body: {request.body.decode('utf-8')}")
        update = json.loads(request.body)
    except json.JSONDecodeError:
        print("❌ JSON Decode Error")
        return JsonResponse({"status": "invalid payload"})

    # Find the bot by token
    from bot_app.models import BotSettings
    bot = BotSettings.objects.filter(telegram_token=token).first()
    
    if not bot:
        print(f"❌ Bot query failed. Token: {token}")
        # If token doesn't match, maybe it's an old webhook? 
        # But for security we should probably ignore or log.
        return JsonResponse({"status": "bot not found"}, status=404)

    print(f"✅ Bot found: {bot.bot_username}")

    # --- Handle message
    if "message" in update:
        print("🔹 Handling Message...")
        handle_message_update(update, bot)

    # --- Handle callback queries (buttons)
    elif "callback_query" in update:
        print("🔹 Handling Callback...")
        handle_callback(update, bot)

    response = JsonResponse({"ok": True})
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    return response
