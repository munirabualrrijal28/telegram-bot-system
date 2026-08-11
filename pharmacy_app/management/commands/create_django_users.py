# pharmacy_app/management/commands/create_django_users.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import TelegramUser
from django.db import transaction

class Command(BaseCommand):
    help = 'Create Django User objects for existing TelegramUser rows and link them'

    def handle(self, *args, **options):
        created = 0
        skipped = 0
        linked = 0

        qs = TelegramUser.objects.all()
        for app in qs:
            if app.user_id:
                skipped += 1
                continue

            # pick a usable username: prefer email, fallback phone, fallback auto id
            username = (app.email or app.phone or f'appuser_{app.id}').strip()
            # username must be <= 150 chars
            username = username[:150]

            # avoid collisions
            orig_username = username
            idx = 1
            while User.objects.filter(username=username).exists():
                username = f"{orig_username}_{idx}"
                idx += 1

            # create a User
            user = User(username=username, email=app.email or '')
            # if TelegramUser.password_hash exists and looks like a Django password hash,
            # copy it so existing passwords continue to work.
            if app.password_hash:
                user.password = app.password_hash
            else:
                user.set_unusable_password()

            # You can optionally set is_staff True for owners (not done automatically).
            # user.is_staff = True
            # user.is_superuser = False

            with transaction.atomic():
                user.save()
                app.user = user
                app.save()
                created += 1
                self.stdout.write(self.style.SUCCESS(f'Linked TelegramUser {app.id} -> User {user.username}'))

        self.stdout.write(self.style.SUCCESS(f'Done. created={created}, skipped={skipped}'))




        
