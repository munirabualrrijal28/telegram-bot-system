# bot_app/urls.py
from django.urls import path
from . import views, views_miniapp
from bot_app.telegram.views import telegram_webhook

app_name = 'bot_app'

urlpatterns = [
    path('bot_app-management/', views.bot_manage_view, name='bot_manage'),

    # FAQ CRUD
    path('bot_app/faqs/list/', views.faq_list, name='faq_list'),
    path('bot_app/faqs/create/', views.faq_create, name='faq_create'),
    path('bot_app/faqs/<uuid:pk>/update/', views.faq_update, name='faq_update'),
    path('bot_app/faqs/<uuid:faq_id>/delete/', views.faq_delete, name='faq_delete'),
    path('bot_app/faqs/<uuid:faq_id>/toggle-status/', views.toggle_faq_status, name='toggle_faq_status'),

    # Category routes
    path("category/list/", views.category_list, name="category_list"),
    path("category/create/", views.category_create, name="category_create"),
    path("category/update/<uuid:pk>/", views.category_update, name="category_update"),
    path("category/delete/<uuid:pk>/", views.category_delete, name="category_delete"),
    path("faq/category/<uuid:category_id>/partial/", views.faq_list_by_category_partial, name="faq_list_by_category_partial"),
    path('faq/<uuid:pk>/', views.faq_detail, name='faq_detail'),

    # Page & Group Management
    path('page/create/', views.page_create, name='page_create'),
    path('page/update/<uuid:pk>/', views.page_update, name='page_update'),
    path('page/delete/<uuid:pk>/', views.page_delete, name='page_delete'),
    path('group/create/', views.group_create, name='group_create'),
    path('group/update/<uuid:pk>/', views.group_update, name='group_update'),
    path('group/detail/<uuid:pk>/', views.group_detail, name='group_detail'),
    path('group/delete/<uuid:pk>/', views.group_delete, name='group_delete'),
    path('attachments/list/', views.get_attachments, name='get_attachments'),

    # Bot Settings
    path('bot-settings/', views.bot_settings_view, name='bot_settings'),
    path('bot-settings/details/<uuid:pk>/', views.bot_get_details, name='bot_get_details'),
    path('bot-settings/test-connection/', views.test_bot_connection, name='test_bot_connection'),
    path("bot-settings/connect_bot/", views.connect_bot, name="connect_bot"),
    path("bot-settings/disconnect_bot/", views.disconnect_bot, name="disconnect_bot"),
    path('bot-settings/verify-password/', views.verify_password, name='verify_password'),
    path('bot-settings/update-keyboard-type/', views.update_keyboard_type, name='update_keyboard_type'),

    # Subscription
    path('subscription/', views.subscription_view, name='subscription'),
    path('subscription/activate/', views.activate_subscription, name='activate_subscription'),

    # Telegram Webhook
    path("telegram-webhook/<str:token>/", telegram_webhook, name="telegram_webhook"),
    
    # Telegram Mini App (public — no login required)
    path("mini-app/page/<uuid:page_id>/", views_miniapp.page_miniapp, name="page_miniapp"),

    # Debug Endpoints
    path("dashboard/debug-errors/", views.debug_errors, name="debug_errors"),
    path("dashboard/debug-tables/", views.debug_tables, name="debug_tables"),
    path("dashboard/fix-tables/", views.fix_tables, name="fix_tables"),
]