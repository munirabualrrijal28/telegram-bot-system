# bot_app/views_miniapp.py
"""
Public views for the Telegram Mini App.
These views are NOT login-protected — they are opened inside Telegram's WebView.
"""
from django.shortcuts import get_object_or_404, render
from django.views.decorators.clickjacking import xframe_options_exempt
from bot_app.models import BotPage


@xframe_options_exempt
def page_miniapp(request, page_id):
    """
    Render the Telegram Mini App for a given BotPage.
    Shows all groups and their items.
    """
    page = get_object_or_404(BotPage, pk=page_id)
    # Do NOT prefetch 'items' here — it evaluates eagerly and crashes if
    # bot_group_item table doesn't exist yet on the production server.
    groups = page.groups.order_by('created_at')
    bot = page.category.bot

    # Build absolute base URL so media image URLs work inside Telegram WebView
    base_url = request.build_absolute_uri('/').rstrip('/')

    groups_data = []
    for group in groups:
        items_data = []
        try:
            # Access items lazily (one query per group — safe if table is missing)
            for item in group.items.order_by('order', 'created_at'):
                image_url = ''
                if item.image:
                    raw_url = item.image.url
                    image_url = raw_url if raw_url.startswith('http') else base_url + raw_url
                items_data.append({
                    'id': str(item.id),
                    'name': item.name,
                    'description': item.description,
                    'image_url': image_url,
                })
        except Exception:
            # bot_group_item table may not exist yet — show group without items
            items_data = []

        group_image_url = ''
        if group.image:
            raw_url = group.image.url
            group_image_url = raw_url if raw_url.startswith('http') else base_url + raw_url

        # Contact: group-specific username OR fallback to bot username
        contact_username = group.contact_bot_username or (bot.bot_username if bot else '')

        groups_data.append({
            'id': str(group.id),
            'name': group.name,
            'image_url': group_image_url,
            'contact_username': contact_username,
            'items': items_data,
        })

    return render(request, 'bot_app/miniapp/page.html', {
        'page': page,
        'groups_data': groups_data,
        'bot': bot,
    })
