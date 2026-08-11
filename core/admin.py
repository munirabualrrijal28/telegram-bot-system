from django.contrib import admin
from core.models import PlanActivationCode, TelegramUser, Workspace, SystemAdmin, Subscription, AuditLog, Attachment

@admin.register(PlanActivationCode)
class PlanActivationCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'plan_name', 'code_type', 'is_used', 'used_by', 'created_at', 'expires_at')
    list_filter = ('plan_name', 'code_type', 'is_used', 'created_at')
    search_fields = ('code', 'target_user__name', 'used_by__name')
    readonly_fields = ('code', 'used_at', 'created_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Code Details', {
            'fields': ('code', 'plan_name', 'code_type', 'target_user', 'expires_at')
        }),
        ('Usage Status', {
            'fields': ('is_used', 'used_by', 'used_at', 'failed_attempts')
        }),
        ('Meta', {
            'fields': ('created_by', 'created_at')
        }),
    )

@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('name', 'telegram_user_id', 'role', 'workspace', 'created_at')
    search_fields = ('name', 'telegram_user_id', 'email')
    list_filter = ('role', 'status')

@admin.register(Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'created_at')
    search_fields = ('name', 'owner__username')

@admin.register(SystemAdmin)
class SystemAdminAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_active')
    list_filter = ('role', 'is_active')

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('workspace', 'plan_name', 'status', 'start_date', 'end_date')
    list_filter = ('status', 'plan_name')

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'actor_type', 'resource_type', 'created_at')
    list_filter = ('action', 'actor_type', 'resource_type')
    readonly_fields = ('created_at',)

@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'created_at')
    list_filter = ('type',)
    readonly_fields = ('created_at',)
