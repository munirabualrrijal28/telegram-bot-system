# pharmacy_app/signals.py
from django.dispatch import receiver
from allauth.socialaccount.signals import social_account_added
from allauth.account.signals import user_signed_up
from core.models import TelegramUser, Workspace


@receiver(social_account_added)
def create_app_user_on_social_signup(sender, request, sociallogin, **kwargs):
    """
    Automatically create TelegramUser profile and Workspace when user signs up via Google OAuth
    """
    user = sociallogin.user
    
    # Check if TelegramUser already exists
    if not hasattr(user, 'telegram_user') or user.telegram_user is None:
        # Get email and name from sociallogin extra_data
        extra_data = sociallogin.account.extra_data
        email = extra_data.get('email', user.email)
        name = extra_data.get('name', user.get_full_name() or user.username)
        
        # Create a default Workspace for the user
        workspace = Workspace.objects.create(
            owner=user,
            name=f"{name}'s Workspace",
            address="To be updated",
            contact_phone="",
            contact_email=email
        )
        
        # Create TelegramUser profile linked to the pharmacy
        TelegramUser.objects.create(
            user=user,
            name=name,
            email=email,
            role='owner',
            status='active',
            workspace=workspace
        )
        print(f"✅ Created TelegramUser and Workspace for {user.username} (Google OAuth)")


@receiver(user_signed_up)
def create_app_user_on_signup(sender, request, user, **kwargs):
    """
    Fallback: Create TelegramUser profile for any new user signup
    """
    if not hasattr(user, 'telegram_user') or user.telegram_user is None:
        # Create a default Workspace
        workspace = Workspace.objects.create(
            owner=user,
            name=f"{user.username}'s Workspace",
            address="To be updated",
            contact_phone="",
            contact_email=user.email
        )
        
        TelegramUser.objects.create(
            user=user,
            name=user.get_full_name() or user.username,
            email=user.email,
            role='owner',
            status='active',
            workspace=workspace
        )
        print(f"✅ Created TelegramUser and Workspace for {user.username}")

