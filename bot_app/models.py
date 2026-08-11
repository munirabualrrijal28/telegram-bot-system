import uuid
import os
from django.contrib.auth.models import User
from django.db import models
from core.models import UUIDModel, Workspace, TelegramUser

class BotSettings(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="bot_settings"
    )

    workspace_name = models.CharField(max_length=255)
    telegram_token = models.CharField(max_length=255, blank=True, null=True)
    bot_username = models.CharField(max_length=255, blank=True, null=True)

    is_active = models.BooleanField(default=False)
    is_connected = models.BooleanField(default=False)

    # -----------------------------
    # 📌 DASHBOARD METRICS FIELDS
    # -----------------------------
    interactions_count = models.PositiveIntegerField(default=0)
    questions_count = models.PositiveIntegerField(default=0)
    active_users_count = models.PositiveIntegerField(default=0)

    # -----------------------------
    # BOT TEXTS
    # -----------------------------
    welcome_message = models.TextField(
        default="👋 Welcome to our bot! How can we help you?"
    )
    fallback_message = models.TextField(
        default="❗Sorry, I couldn't find an answer to that."
    )
    
    start_keywords = models.TextField(
        default="hi,hello,hey,start,Hi,Hello,Hey,Start,مرحبا,السلام عليكم,أهلا,اهلا,أهلا وسهلا",
        help_text="Comma-separated list of keywords that trigger the welcome message",
        blank=True
    )

    # -----------------------------
    # WORKING HOURS
    # -----------------------------
    working_hours_start = models.TimeField(default="08:00")
    working_hours_end = models.TimeField(default="22:00")

    # -----------------------------
    # LANGUAGE
    # -----------------------------
    language = models.CharField(
        max_length=20,
        default="en",
        choices=[
            ('en', 'English'),
            ('ar', 'Arabic'),
        ],
    )

    # -----------------------------
    # CONTACT INFORMATION
    # -----------------------------
    show_contact_info = models.BooleanField(default=True)
    contact_phone = models.CharField(max_length=50, blank=True, null=True)
    contact_address = models.CharField(max_length=255, blank=True, null=True)
    google_maps_link = models.URLField(blank=True, null=True)

    enable_ai_mode = models.BooleanField(default=False)

    # -----------------------------
    # KEYBOARD SETTINGS
    # -----------------------------
    KEYBOARD_CHOICES = [
        ('INLINE', 'Inline Keyboard'),
        ('REPLY', 'Reply Keyboard'),
    ]
    home_keyboard_type = models.CharField(
        max_length=10,
        choices=KEYBOARD_CHOICES,
        default='INLINE',
        help_text="Default keyboard style for the main menu"
    )

    # -----------------------------
    # TIMESTAMPS
    # -----------------------------
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # -----------------------------
    # ❗ NOT saved to DB
    # -----------------------------
    temp_token = None
    temp_username = None

    def __str__(self):
        return f"{self.workspace_name} Bot Settings"

    class Meta:
        db_table = "bot_settings"
        indexes = [
            models.Index(fields=["workspace_name"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["is_connected"]),
        ]

class FAQCategory(UUIDModel):
    """Category (supports subcategories via parent). Linked to Pharmacy via string FK to avoid circular imports."""
    bot = models.ForeignKey(
        BotSettings,
        on_delete=models.CASCADE,
        related_name='categories',
        null=True,
        blank=True,
        help_text="Bot this category belongs to"
    )
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='bot_faq_categories')
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='subcategories')
    
    KEYBOARD_CHOICES = [
        ('INLINE', 'Inline Keyboard'),
        ('REPLY', 'Reply Keyboard'),
    ]
    keyboard_type = models.CharField(
        max_length=10,
        choices=KEYBOARD_CHOICES,
        default='INLINE',
        help_text="How to display subcategories/questions for this category"
    )

    class Meta:
        db_table = 'bot_faq_category'
        ordering = ['name']
        indexes = [
            models.Index(fields=['bot'], name='idx_faqcat_bot'),
        ]

    def __str__(self):
        return self.name if not self.parent else f"{self.parent.name} → {self.name}"

class FAQ(UUIDModel):
    """FAQ tied to a Pharmacy and optional category. Keep id stable (UUID)."""
    bot = models.ForeignKey(
        BotSettings,
        on_delete=models.CASCADE,
        related_name='faqs',
        null=True,
        blank=True,
        help_text="Bot this FAQ belongs to"
    )
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='bot_faqs')
    category = models.ForeignKey(FAQCategory, null=True, blank=True, on_delete=models.SET_NULL, related_name='faqs')

    question = models.TextField()
    answer = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bot_faq'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['bot'], name='idx_faq_bot'),
        ]

    def __str__(self):
        return self.question[:80]



class BotPage(UUIDModel):
    """
    A Page within a Category.
    Pages act as containers for Groups.
    """
    category = models.ForeignKey(
        FAQCategory,
        on_delete=models.CASCADE,
        related_name='pages',
        help_text="Category this page belongs to"
    )
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bot_page'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.name} (in {self.category.name})"

class PageGroup(UUIDModel):
    """
    A Group within a Page.
    Groups contain a collection of Attachments.
    """
    page = models.ForeignKey(
        BotPage,
        on_delete=models.CASCADE,
        related_name='groups',
        help_text="Page this group belongs to"
    )
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='group_images/', null=True, blank=True)
    contact_bot_username = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        help_text="Bot username to contact (without @). If empty, uses the main bot."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bot_page_group'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.name} (in {self.page.name})"


class GroupItem(UUIDModel):
    """
    An item belonging to a PageGroup.
    Replaces the M2M approach (medicines/attachments) with a direct FK model
    that has no join table — fully portable across environments.
    """
    group = models.ForeignKey(
        PageGroup,
        on_delete=models.CASCADE,
        related_name='items',
        help_text="Group this item belongs to"
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='group_item_images/', null=True, blank=True)
    order = models.PositiveIntegerField(default=0, help_text="Display order within the group")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bot_group_item'
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.name} (in group: {self.group.name})"
