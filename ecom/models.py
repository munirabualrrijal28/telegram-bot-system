# ecom/models.py
"""
E-commerce models: Product catalog, inventory, and order management.
"""

import os
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver

# Import from core app
from core.models import UUIDModel, Workspace, TelegramUser


# ============================================================================
# PRODUCT CATALOG
# ============================================================================

class Category(UUIDModel):
    """Product categories"""
    workspace = models.ForeignKey(
        Workspace, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL, 
        related_name='categories'
    )
    name = models.CharField(max_length=200)
    slug = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "category"
        indexes = [
            models.Index(fields=['name'], name='idx_category_name'),
        ]


class Medicine(UUIDModel):
    """Product catalog - medicines"""
    bot = models.ForeignKey(
        'bot_app.BotSettings',
        on_delete=models.CASCADE,
        related_name='medicines',
        null=True,
        blank=True,
        help_text="Bot this medicine belongs to"
    )
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='medicines')
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL, related_name='medicines')
    sku = models.CharField(max_length=100, null=True, blank=True, unique=True)
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=200, null=True, blank=True)
    generic_name = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    dosage_form = models.CharField(max_length=100, null=True, blank=True)
    strength = models.CharField(max_length=100, null=True, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    visible = models.BooleanField(default=True)
    stock_quantity = models.IntegerField(default=0)
    low_stock_threshold = models.IntegerField(default=0)
    image = models.ImageField(upload_to="medicines/", blank=True, null=True)
    metadata = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = "medicine"
        indexes = [
            models.Index(fields=['workspace'], name='idx_medicine_workspace_id'),
            models.Index(fields=['bot'], name='idx_medicine_bot'),
        ]


@receiver(post_delete, sender=Medicine)
def delete_medicine_image(sender, instance, **kwargs):
    """Delete image file when Medicine is deleted"""
    if instance.image:
        image_path = instance.image.path
        if os.path.isfile(image_path):
            os.remove(image_path)


class PriceHistory(UUIDModel):
    """Price change tracking"""
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='price_history')
    old_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    new_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    changed_by_user = models.ForeignKey(TelegramUser, null=True, blank=True, on_delete=models.SET_NULL)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "price_history"
        indexes = [
            models.Index(fields=['medicine'], name='idx_pricehistory_medicine'),
            models.Index(fields=['changed_at'], name='idx_pricehistory_changed_at'),
        ]


# ============================================================================
# INVENTORY MANAGEMENT
# ============================================================================

class InventoryTransaction(UUIDModel):
    """Stock movement tracking"""
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    delta = models.IntegerField()
    reason = models.CharField(max_length=50)
    reference_id = models.CharField(max_length=36, null=True, blank=True)
    performed_by = models.ForeignKey(TelegramUser, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "inventory_transaction"
        indexes = [
            models.Index(fields=['medicine'], name='idx_invtrans_medicine'),
            models.Index(fields=['workspace'], name='idx_invtrans_workspace'),
            models.Index(fields=['performed_by'], name='idx_invtrans_performed_by'),
        ]


# ============================================================================
# ORDER MANAGEMENT
# ============================================================================

class Order(UUIDModel):
    """Customer orders"""
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='orders')
    user = models.ForeignKey(TelegramUser, null=True, blank=True, on_delete=models.SET_NULL, related_name='orders')
    medicine = models.ForeignKey(Medicine, null=True, blank=True, on_delete=models.SET_NULL, related_name='orders')
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, default='pending')
    metadata = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "order"
        indexes = [
            models.Index(fields=['status'], name='idx_order_status'),
            models.Index(fields=['workspace'], name='idx_order_workspace'),
        ]


class OrderItem(UUIDModel):
    """Order line items"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = "order_item"
        indexes = [
            models.Index(fields=['medicine'], name='idx_orderitem_medicine'),
        ]
