import requests
from django.core.management.base import BaseCommand
from bot_app.models import BotSettings
import os

class Command(BaseCommand):
    help = 'Re-registers webhooks for all connected bots to the production domain'

    def handle(self, *args, **options):
        bots = BotSettings.objects.filter(is_connected=True)
        domain = "mytelebot.com"
        
        self.stdout.write(f"Found {bots.count()} connected bots. Registering webhooks to {domain}...")
        
        success_count = 0
        for bot in bots:
            webhook_url = f"https://{domain}/telegram-webhook/{bot.telegram_token}/"
            url = f"https://api.telegram.org/bot{bot.telegram_token}/setWebhook?url={webhook_url}"
            try:
                resp = requests.get(url, timeout=10).json()
                if resp.get('ok'):
                    self.stdout.write(self.style.SUCCESS(f"Successfully set webhook for @{bot.bot_username}"))
                    success_count += 1
                else:
                    self.stdout.write(self.style.ERROR(f"Failed to set webhook for @{bot.bot_username}: {resp.get('description')}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error setting webhook for @{bot.bot_username}: {str(e)}"))
                
        self.stdout.write(self.style.SUCCESS(f"\nCompleted! {success_count}/{bots.count()} webhooks updated."))
