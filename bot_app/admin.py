# bot_app/admin.py
from django.contrib import admin
from core.models import Workspace, TelegramUser, Attachment
from ecom.models import Medicine, Category, Order, OrderItem
from bot_app.models import FAQCategory, FAQ, BotSettings


@admin.register(FAQCategory)
class FAQCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'workspace')
    list_filter = ('workspace',)
    search_fields = ('name',)


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'category', 'is_active', 'created_at')
    list_filter = ('is_active', 'category', 'workspace')
    search_fields = ('question', 'answer')
    date_hierarchy = 'created_at'


@admin.register(BotSettings)
class BotSettingsAdmin(admin.ModelAdmin):
    list_display = ('workspace_name', 'bot_username', 'is_active', 'is_connected', 'owner')
    list_filter = ('is_active', 'is_connected', 'language')
    search_fields = ('workspace_name', 'bot_username')
    readonly_fields = ('created_at', 'updated_at')