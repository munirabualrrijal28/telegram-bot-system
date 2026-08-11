from django.core.management.base import BaseCommand
from core.models import SystemAdmin
from django.contrib.auth.hashers import make_password

class Command(BaseCommand):
    help = 'Seeds the database with a System Admin user'

    def handle(self, *args, **options):
        # Configuration - Change these values to add different admins
        USERNAME = 'munir28'
        EMAIL = 'moneermoneer28@gmail.com'
        PASSWORD = '777928412'

        self.stdout.write(f"Checking for existing admin: {USERNAME} / {EMAIL}")

        if SystemAdmin.objects.filter(username=USERNAME).exists():
            self.stdout.write(self.style.WARNING(f"Admin with username '{USERNAME}' already exists."))
            return

        if SystemAdmin.objects.filter(email=EMAIL).exists():
            self.stdout.write(self.style.WARNING(f"Admin with email '{EMAIL}' already exists."))
            return

        # Create new admin
        try:
            admin = SystemAdmin(
                username=USERNAME,
                email=EMAIL,
                password_hash=make_password(PASSWORD),
                role='moderator', # Default role, change if needed
                is_active=True
            )
            admin.save()
            self.stdout.write(self.style.SUCCESS(f"Successfully created admin: {USERNAME}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to create admin: {str(e)}"))
