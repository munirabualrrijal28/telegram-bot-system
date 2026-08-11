# pharmacy_app/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

from django.urls import path, include


app_name = 'pharmacy_app'


urlpatterns = [
    path("login/", views.owner_login, name="owner_login"),
    path("signup/", views.owner_signup, name="owner_signup"),
    path("logout/", views.owner_logout, name="owner_logout"),
    path("dashboard/", views.owner_dashboard, name="owner_dashboard"),

    # Attachments page with tabs (General + Medicines)
    path("attachments/", views.attachments_page, name="attachments_page"),

    # path('dashboard/', include('bot_app.urls', namespace='bot_app'))


# 
    path("medicines/", views.medicines_list, name="medicines_list"),
    #  path("medicines/", views.medicines_list, name="medicines_list"),
    path("medicines/add/", views.medicine_add, name="medicine_add"),
    path("medicines/<uuid:pk>/edit/", views.medicine_edit, name="medicine_edit"),
    path("medicines/<uuid:pk>/delete/", views.medicine_delete, name="medicine_delete"),


    path("medicines/autocomplete/", views.medicines_autocomplete, name="medicines_autocomplete"),

  # inline stock update

    path("medicines/<uuid:pk>/update-stock/", views.update_stock, name="update_stock"),

    path("medicines/export-csv/", views.export_medicines_csv, name="medicine_export_csv"),
    
    # New import endpoints with column mapping and preview
    path("medicines/import/upload/", views.medicine_import_upload, name="medicine_import_upload"),
    path("medicines/import/preview/", views.medicine_import_preview, name="medicine_import_preview"),
    path("medicines/import/process/", views.medicine_import_process, name="medicine_import_process"),
    
    # Temp file upload for FilePond
    path("upload-temp-image/", views.upload_temp_image, name="upload_temp_image"),
    path("delete-temp-image/", views.delete_temp_image, name="delete_temp_image"),


]

