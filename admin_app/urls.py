from django.urls import path
from . import views

app_name = 'admin_app'

urlpatterns = [
    path('', views.admin_login, name='login'), # /admin-login/ -> Login
    path('logout/', views.admin_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    # Subscriptions Page
    path('subscriptions/', views.subscription_list, name='subscription_list'),
    path('subscriptions/<uuid:user_id>/update/', views.subscription_update, name='subscription_update'),


    # Subscriptions Page/Codes Urls 
    path('activation-codes/', views.activation_codes, name='activation_codes'),
    path('activation-codes/create/', views.create_activation_code, name='create_activation_code'),
    path('activation-codes/<uuid:pk>/update/', views.update_activation_code, name='update_activation_code'),
    path('activation-codes/<uuid:pk>/delete/', views.delete_activation_code, name='delete_activation_code'),
    # 
        path('broadcast/', views.broadcast, name='broadcast'),

    path('users/<uuid:user_id>/manage/', views.user_manage, name='user_manage'),
    
    # User Management List & Actions
    path('users/', views.users_list, name='users_list'),
    path('users/<uuid:user_id>/freeze/', views.user_freeze, name='user_freeze'),
    path('users/<uuid:user_id>/unfreeze/', views.user_unfreeze, name='user_unfreeze'),
    path('users/<uuid:user_id>/details/', views.user_details_ajax, name='user_details_ajax'),
]
