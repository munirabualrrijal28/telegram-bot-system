# core/models.py
"""
Core foundational models used across the entire system.
These are the base models that other apps will import and reference.
"""

import uuid
import os
import secrets
import string
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_delete
from django.dispatch import receiver


# ============================================================================
# ABSTRACT BASE CLASS
# ============================================================================

class UUIDModel(models.Model):
    """Abstract base class providing UUID primary key for all models"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    class Meta:
        abstract = True


# ============================================================================
# CORE TENANT MODEL
# ============================================================================

class Workspace(UUIDModel):
    """
    Main tenant model - the workspace entity.
    Most other models will reference this via ForeignKey.
    Domain-agnostic: can represent any business or individual bot workspace.
    """
    owner = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='workspace', 
        null=True,
        blank=True
    )
    name = models.CharField(max_length=255)
    address = models.TextField(null=True, blank=True)
    contact_phone = models.CharField(max_length=32, null=True, blank=True)
    contact_email = models.EmailField(null=True, blank=True)
    logo_url = models.CharField(max_length=500, null=True, blank=True)
    hours = models.JSONField(null=True, blank=True)
    settings = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "workspace"

    def __str__(self):
        return self.name


# ============================================================================
# SYSTEM ADMINISTRATION
# ============================================================================

class SystemAdmin(UUIDModel):
    """System-level administrator accounts"""
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(null=True, blank=True, unique=True)
    password_hash = models.CharField(max_length=255)
    role = models.CharField(max_length=32, default='moderator')
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "system_admin"  # Keep existing table name


# ============================================================================
# APPLICATION USER
# ============================================================================

class TelegramUser(UUIDModel):
    """
    Generalized application user profile.
    Links Django's User model with Telegram user ID.
    """
    user = models.OneToOneField(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='telegram_user'
    )
    telegram_user_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=32, null=True, blank=True)
    password_hash = models.CharField(max_length=255, null=True, blank=True)
    role = models.CharField(max_length=32, default='customer')
    workspace = models.ForeignKey(
        Workspace, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL, 
        related_name='users'
    )
    status = models.CharField(max_length=20, default='active')
    has_used_free_trial = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "telegram_user"  # Renamed from app_user
        indexes = [
            models.Index(fields=['telegram_user_id'], name='idx_tg_user_telegram'),
            models.Index(fields=['email'], name='idx_tg_user_email'),
            models.Index(fields=['phone'], name='idx_tg_user_phone'),
            models.Index(fields=['role'], name='idx_tg_user_role'),
        ]


# ============================================================================
# AUDIT & LOGGING
# ============================================================================

class AuditLog(UUIDModel):
    """System-wide action logging"""
    actor_type = models.CharField(max_length=32)
    actor_id = models.CharField(max_length=36, null=True, blank=True)
    action = models.CharField(max_length=200)
    resource_type = models.CharField(max_length=100)
    resource_id = models.CharField(max_length=36, null=True, blank=True)
    details = models.JSONField(null=True, blank=True)
    ip_address = models.CharField(max_length=45, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "audit_log"  # Keep existing table name
        indexes = [
            models.Index(fields=['actor_type', 'actor_id'], name='idx_audit_actor'),
            models.Index(fields=['resource_type', 'resource_id'], name='idx_audit_resource'),
            models.Index(fields=['created_at'], name='idx_audit_created_at'),
        ]


# ============================================================================
# SUBSCRIPTION MANAGEMENT
# ============================================================================

# ============================================================================
# SUBSCRIPTION MANAGEMENT
# ============================================================================

class PlanActivationCode(UUIDModel):
    """
    Unified activation code for subscription plans.
    Replaces admin_app.ActivationCode and bot_app.SubscriptionCode.
    """
    PLAN_CHOICES = [
        ('Free', 'Free Plan'),
        ('Free Trial', 'Free Trial (7 Days)'),
        ('Pro', 'Pro Plan'),
        ('Max', 'Max Plan'),
    ]
    
    CODE_TYPE_CHOICES = [
        ('general', 'General Code'),
        ('user_specific', 'User-Specific Code'),
    ]
    
    code = models.CharField(max_length=50, unique=True, editable=False, db_index=True)
    plan_name = models.CharField(max_length=20, choices=PLAN_CHOICES)
    code_type = models.CharField(max_length=20, choices=CODE_TYPE_CHOICES, default='general')
    
    # Target user for user-specific codes
    target_user = models.ForeignKey('core.TelegramUser', on_delete=models.CASCADE, null=True, blank=True, related_name='targeted_activation_codes')
    
    # Usage tracking
    is_used = models.BooleanField(default=False)
    used_by = models.ForeignKey('core.TelegramUser', on_delete=models.SET_NULL, null=True, blank=True, related_name='used_activation_codes')
    used_at = models.DateTimeField(null=True, blank=True)
    
    # Creation tracking
    created_by = models.ForeignKey('core.SystemAdmin', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'plan_activation_code'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['code'], name='idx_plan_code'),
            models.Index(fields=['is_used'], name='idx_plan_is_used'),
            models.Index(fields=['expires_at'], name='idx_plan_expires'),
        ]

    def __str__(self):
        # Security: Never show full code in logs/string representation
        return f"{self.code[:4]}... - {self.plan_name}"

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_secure_code()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_secure_code():
        """
        Generate a secure, random activation code.
        Requirements: Random (>= 128 bits entropy), Uppercase + digits.
        Alphabet size: 36 (A-Z, 0-9).
        Entropy = log2(36^N). For 128 bits: N >= 128 / 5.17 ~= 24.75.
        We use 25 characters formatted as 5 groups of 5: XXXXX-XXXXX-XXXXX-XXXXX-XXXXX.
        """
        chars = string.ascii_uppercase + string.digits
        # Generate 5 groups of 5 characters
        groups = [''.join(secrets.choice(chars) for _ in range(5)) for _ in range(5)]
        return '-'.join(groups)


class Subscription(UUIDModel):
    """Workspace subscription tracking"""
    workspace = models.ForeignKey(
        Workspace, 
        on_delete=models.CASCADE, 
        related_name='subscriptions'
    )
    plan_name = models.CharField(max_length=100)
    status = models.CharField(max_length=20, default='active')  # active, expired, cancelled
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "subscription"  # Keep existing table name
        indexes = [
            models.Index(fields=['workspace'], name='idx_subscription_workspace'),
            models.Index(fields=['status'], name='idx_subscription_status'),
            models.Index(fields=['end_date'], name='idx_subscription_end'),
        ]


# ============================================================================
# FILE ATTACHMENTS
# ============================================================================

class Attachment(models.Model):
    """Generalized file utility for attachments"""
    TYPE_CHOICES = [
        ('GENERAL', 'General'),
        ('MEDICINE', 'Medicine'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='attachments/')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='GENERAL')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attachments')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'attachment'  # Keep existing table name
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owner'], name='idx_attachment_owner'),
            models.Index(fields=['type'], name='idx_attachment_type'),
        ]
    
    def __str__(self):
        return self.title


# ============================================================================
# SIGNALS
# ============================================================================

@receiver(post_delete, sender=Attachment)
def delete_attachment_image(sender, instance, **kwargs):
    """Delete attachment image file when Attachment is deleted"""
    if instance.image and os.path.isfile(instance.image.path):
        os.remove(instance.image.path)
