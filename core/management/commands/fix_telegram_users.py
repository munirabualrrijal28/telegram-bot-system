from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import TelegramUser, Workspace

class Command(BaseCommand):
    help = 'Create TelegramUser profiles for existing Django users'

    def handle(self, *args, **options):
        users = User.objects.all()
        created_count = 0
        linked_count = 0

        for user in users:
            # Check if TelegramUser exists
            if hasattr(user, 'telegram_user'):
                self.stdout.write(self.style.SUCCESS(f'User {user.username} already has a TelegramUser profile.'))
                continue

            # Check if TelegramUser exists by email (legacy/broken link)
            tg_user = TelegramUser.objects.filter(email=user.email).first()
            
            if tg_user:
                tg_user.user = user
                tg_user.save()
                linked_count += 1
                self.stdout.write(self.style.SUCCESS(f'Linked existing TelegramUser to {user.username}'))
            else:
                # Create new TelegramUser
                # Ensure workspace exists
                workspace = getattr(user, 'workspace', None)
                if not workspace:
                    workspace = Workspace.objects.create(
                        name=f"{user.username}'s Workspace",
                        owner=user
                    )
                    self.stdout.write(self.style.SUCCESS(f'Created workspace for {user.username}'))

                TelegramUser.objects.create(
                    user=user,
                    email=user.email,
                    name=user.get_full_name() or user.username,
                    role='owner', # Default to owner for existing users to ensure access
                    workspace=workspace,
                    status='active'
                )
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created new TelegramUser for {user.username}'))

        self.stdout.write(self.style.SUCCESS(f'Process completed. Created: {created_count}, Linked: {linked_count}'))
