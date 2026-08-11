# bot_app/middleware.py
"""
Middleware to manage bot selection across the application.
Stores the selected bot in the session and makes it available to all views.
"""
from bot_app.models import BotSettings


class BotSelectionMiddleware:
    """
    Middleware that manages bot selection for authenticated users.
    
    - Retrieves selected bot from query params or session
    - Auto-selects first bot if none is selected
    - Makes selected bot available as request.selected_bot
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Log every request to debug_log.txt
        with open("debug_log.txt", "a", encoding="utf-8") as f:
            f.write(f"REQUEST: {request.method} {request.path}\n")
            
        # Only process for authenticated users
        if request.user.is_authenticated:
            selected_bot = None
            
            # Check if bot_id is in query params (user just selected a bot)
            bot_id = request.GET.get('bot_id')
            
            if bot_id:
                # User explicitly selected a bot
                try:
                    selected_bot = BotSettings.objects.get(
                        id=bot_id,
                        owner=request.user
                    )
                    # Store in session for persistence
                    request.session['selected_bot_id'] = str(selected_bot.id)
                except BotSettings.DoesNotExist:
                    # Invalid bot_id, clear session
                    request.session.pop('selected_bot_id', None)
            
            # If no bot selected from query param, check session
            if not selected_bot:
                session_bot_id = request.session.get('selected_bot_id')
                if session_bot_id:
                    try:
                        selected_bot = BotSettings.objects.get(
                            id=session_bot_id,
                            owner=request.user
                        )
                    except BotSettings.DoesNotExist:
                        # Stored bot no longer exists, clear session
                        request.session.pop('selected_bot_id', None)
            
            # If still no bot, auto-select first bot for this user
            if not selected_bot:
                first_bot = BotSettings.objects.filter(owner=request.user).first()
                if first_bot:
                    selected_bot = first_bot
                    request.session['selected_bot_id'] = str(first_bot.id)
            
            # Make selected bot available to all views
            request.selected_bot = selected_bot
        else:
            request.selected_bot = None
        
        response = self.get_response(request)
        return response
