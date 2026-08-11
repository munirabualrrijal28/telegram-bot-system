# bot_app/context_processors.py
"""
Context processor to make bot selection available globally in all templates.
"""
from bot_app.models import BotSettings


def bot_context(request):
    """
    Add bot selection context to all templates.
    
    Makes available:
    - selected_bot: The currently selected bot (or None)
    - user_bots: All bots owned by the current user
    
    Usage in templates:
        {% if selected_bot %}
            Current bot: {{ selected_bot.bot_username }}
        {% endif %}
        
        <select>
            {% for bot in user_bots %}
                <option value="{{ bot.id }}">{{ bot.workspace_name }}</option>
            {% endfor %}
        </select>
    """
    if not request.user.is_authenticated:
        return {}
    
    return {
        'selected_bot': getattr(request, 'selected_bot', None),
        'user_bots': BotSettings.objects.filter(owner=request.user).order_by('workspace_name'),
    }
