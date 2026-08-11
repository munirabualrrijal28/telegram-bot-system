# from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
# import csv
# import io
# import re

import csv, io, re 
# Create your views here.
# pharmacy_app/views.py
from functools import wraps
from django.http import HttpResponseForbidden
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from core.models import Workspace, TelegramUser, Attachment
from ecom.models import Medicine, Category, Order, OrderItem

from django.db.models import Sum, F, Q


from django.contrib.auth.decorators import login_required

from django.utils.timezone import now
from django.db.models.functions import TruncDate


from django.contrib.auth import authenticate, login , logout
from django.urls import reverse


from django import forms
# 

from .forms import MedicineForm   # <-- import form here

import uuid, os
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.core.files import File

from django.http import JsonResponse
from django.conf import settings

import shutil

from django.views.decorators.csrf import csrf_exempt

from django.utils.text import slugify

from django.core.paginator import Paginator



from django.views.decorators.http import require_POST
from django.template.loader import render_to_string


from bot_app.models import FAQCategory, FAQ, BotSettings
from django.contrib.auth.models import User
# ---------
# --------------
# Helper decorator (simple session-based owner check)
# -----------------------


# -----------------------
# owner_required: uses Django request.user then resolves TelegramUser
# -----------------------
def owner_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        # if user is not authenticated, redirect to login with next
        if not request.user.is_authenticated:
            return redirect(f"{reverse('pharmacy_app:owner_login')}?next={request.path}")

        # try to find the linked TelegramUser
        app_user = None
        try:
            app_user = TelegramUser.objects.get(user=request.user)
        except TelegramUser.DoesNotExist:
            # fallback: try match by email and auto link if found
            if request.user.email:
                app_user = TelegramUser.objects.filter(email=request.user.email).first()
                if app_user:
                    app_user.user = request.user
                    app_user.save()

        if not app_user:
            return HttpResponseForbidden("No TelegramUser profile associated with your account.")

        if not app_user.workspace:
            return HttpResponseForbidden("You are not associated with any workspace.")

        # optional role check
        if app_user.role not in ('owner', 'pharmacy_owner', 'institute', 'pharmacy'):
            return HttpResponseForbidden("Unauthorized role.")

        request.app_user = app_user
        request.workspace = app_user.workspace
        return view_func(request, *args, **kwargs)
    return _wrapped



# -----------------------
# Simple login (dev-friendly)
# -----------------------
#     """
#     Simple login for TelegramUser-based owner accounts.
#     Expects POST with 'email' and 'password'.
#     Compares password with TelegramUser.password_hash using Django check_password.
#     NOTE: For production, integrate with django.contrib.auth properly.
#     """

 


# -----------------------
# Login / Logout views using Django auth
# -----------------------
def owner_login(request):
    # handle POST -> authenticate & login
    # preserve 'next' param:
    next_url = request.POST.get('next') or request.GET.get('next') or reverse('pharmacy_app:owner_dashboard')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()

        # Try to find a User by email first
        from django.contrib.auth.models import User
        user = None
        if email:
            user = User.objects.filter(email__iexact=email).first()
            # if not found, try username
            if not user:
                user = User.objects.filter(username__iexact=email).first()

        if user:
            auth_user = authenticate(request, username=user.username, password=password)
            if auth_user is not None:
                login(request, auth_user)
                return redirect(next_url)

        messages.error(request, "Invalid credentials.")
        return render(request, 'owner/auth/auth.html', {"next": next_url, "show_signup": False})

    return render(request, 'owner/auth/auth.html', {"next": next_url, "show_signup": False})



def owner_signup(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        if not email or not password:
            messages.error(request, "Email and password are required.")
            return render(request, 'owner/auth/auth.html', {"show_signup": True})

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'owner/auth/auth.html', {"show_signup": True})

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, 'owner/auth/auth.html', {"show_signup": True})

        # Create user
        try:
            user = User.objects.create_user(username=email, email=email, password=password)
            user.first_name = name
            user.save()
            
            # Create a default Workspace for the new owner
            workspace = Workspace.objects.create(
                name=f"{name}'s Workspace" if name else "My Workspace",
                owner=user
            )

            # Create TelegramUser linked to User and Workspace
            TelegramUser.objects.create(
                user=user, 
                email=email, 
                name=name,
                role='owner',
                workspace=workspace
            )

            login(request, user)
            return redirect('pharmacy_app:owner_dashboard')
        except Exception as e:
            messages.error(request, f"Error creating account: {e}")
            return render(request, 'owner/auth/auth.html', {"show_signup": True})

    return render(request, 'owner/auth/auth.html', {"show_signup": True})


def owner_logout(request):
    # request.session.pop('app_user_id', None)
    # return redirect('pharmacy_app:login')
    logout(request)
    return redirect('pharmacy_app:owner_login')




# -----------------------
# Dashboard view
# -----------------------

# -----------------------
# Dashboard view (use owner_required)
# -----------------------

# old version 11/19/2025 4:38 AM
# @owner_required
# def owner_dashboard(request):
#     pharmacy = request.pharmacy    # set by owner_required

#     today = now().date()

#     # Sales today (use actual field names from your models)
#     sales_today = (
#         Order.objects.filter(pharmacy=pharmacy, created_at__date=today, status__in=['Completed','fulfilled','completed'])
#         .aggregate(total=Sum('total_price'))
#         .get('total') or 0
#     )

#     total_orders = Order.objects.filter(pharmacy=pharmacy).count()
#     total_sales = (
#         Order.objects.filter(pharmacy=pharmacy, status__in=['Completed','fulfilled','completed'])
#         .aggregate(total=Sum('total_price'))
#         .get('total') or 0
#     )

#     total_medicines = pharmacy.medicines.count()
#     # low stock using stock_quantity and low_stock_threshold
#     from django.db.models import F as DjangoF
#     low_stock = pharmacy.medicines.filter(stock_quantity__lt=DjangoF('low_stock_threshold')).count()

#     pending_orders = Order.objects.filter(pharmacy=pharmacy, status__in=['pending','processing']).count()
#     completed_orders = Order.objects.filter(pharmacy=pharmacy, status__in=['completed','fulfilled']).count()

#     recent_orders = (
#         Order.objects.filter(pharmacy=pharmacy).select_related('user').order_by('-created_at')[:10]
#     )

#     # Sales trend (last 7 days)
#     sales_data_qs = (
#         Order.objects.filter(pharmacy=pharmacy, status__in=['Completed','completed','fulfilled'])
#         .annotate(date=TruncDate('created_at'))
#         .values('date')
#         .annotate(total=Sum('total_price'))
#         .order_by('date')[:7]
#     )

#     chart_labels = [entry['date'].strftime("%b %d") for entry in sales_data_qs]
#     chart_values = [float(entry['total']) for entry in sales_data_qs]

    # from bot_app.models import FAQCategory, FAQ, BotSettings
    # from django.contrib.auth.models import User

#     total_categories = FAQCategory.objects.count()
#     total_faqs = FAQ.objects.count()

#     active_users = User.objects.filter(is_active=True).count()

#     # # Optional: interaction counter from your logs table (or set to 0 for now)
#     bot_interactions = BotSettings.objects.first().interactions_count if BotSettings.objects.exists() else 0


#     context = {
#         'pharmacy': pharmacy,
#         'sales_today': sales_today,
#         'total_orders': total_orders,
#         'total_sales': total_sales,
#         'total_medicines': total_medicines,
#         'low_stock': low_stock,
#         'pending_orders': pending_orders,
#         'completed_orders': completed_orders,
#         'recent_orders': recent_orders,
#         'chart_labels': chart_labels,
#         'chart_values': chart_values,
# # ------- bot stats -------
#     "total_categories": total_categories,
#     "categories_added_this_week": 2,   # TODO: calculate dynamically

#     "total_faqs": total_faqs,
#     "faqs_added_this_week": 8,         # TODO: calculate dynamically

#     "active_users": active_users,
#     "active_users_growth": 15,         # placeholder % until you add tracking

#     "bot_interactions": bot_interactions,
#     "bot_interactions_growth": 23,     # placeholder for now
#     }
#     return render(request, 'owner/dashboard.html', context)


@owner_required
def owner_dashboard(request):
    """Dashboard view showing bot-specific metrics."""
    workspace = request.user.workspace
    selected_bot = request.selected_bot  # From middleware
    
    # Calculate metrics for SELECTED BOT only
    if selected_bot:
        total_categories = FAQCategory.objects.filter(bot=selected_bot).count()
        total_faqs = FAQ.objects.filter(bot=selected_bot).count()
        total_medicines = Medicine.objects.filter(bot=selected_bot).count()
        from django.db.models import F
        low_stock_count = Medicine.objects.filter(
            bot=selected_bot,
            stock_quantity__lte=F('low_stock_threshold')
        ).count()
        
        # Bot interaction metrics
        bot_interactions = selected_bot.interactions_count
        active_users = selected_bot.active_users_count
    else:
        # No bot selected - show zeros
        total_categories = 0
        total_faqs = 0  
        total_medicines = 0
        low_stock_count = 0
        bot_interactions = 0
        active_users = 0
    
    context = {
        "total_categories": total_categories,
        "total_faqs": total_faqs,
        "total_medicines": total_medicines,
        "low_stock_count": low_stock_count,
        "bot_interactions": bot_interactions,
        "active_users": active_users,
    }
    
    return render(request, 'owner/dashboard/dashboard.html', context)




# -----------------------
# Medicines list (skeleton) - protect with owner_required
# -----------------------

# @owner_required
# def medicines_list(request):
#     pharmacy = request.pharmacy
#     q = request.GET.get('q', '').strip()
#     qs = pharmacy.medicines.all().order_by('name')

#     if q:
#         qs = qs.filter(Q(name__icontains=q) | Q(sku__icontains=q) | Q(brand__icontains=q))

#     # pagination could be added later
#     medicines = qs[:200]

#     context = {
#         'pharmacy': pharmacy,
#         'medicines': medicines,
#         'q': q,
#     }
#     return render(request, 'owner/medicines_list.html', context)



# Helpers
def _get_request_workspace(request):
    """
    حاول استنتاج مساحة العمل من request.user.telegram_user.workspace
    يمكن تعديل هذه الدالة حسب منطق مشروعك.
    """
    app_user = getattr(request.user, "telegram_user", None)
    if app_user:
        return getattr(app_user, "workspace", None)
    return None


@login_required
def medicines_list(request):
    workspace = _get_request_workspace(request)

    q = request.GET.get("q", "").strip()
    medicines_qs = Medicine.objects.all().order_by("name")
    if workspace:
        medicines_qs = medicines_qs.filter(workspace=workspace)

    if q:
        medicines_qs = medicines_qs.filter(
            Q(name__icontains=q) |
            Q(sku__icontains=q) |
            Q(brand__icontains=q) |
            Q(generic_name__icontains=q)
        )

    paginator = Paginator(medicines_qs, 10)  # 10 per page, عدّل حسب الرغبة
    page_number = request.GET.get("page")
    medicines_page = paginator.get_page(page_number)

    return render(request, "owner/medicines/medicines_list.html", {
        "medicines": medicines_page,
        "q": q,
        "workspace": workspace,
        "form": MedicineForm(), # Pass empty form for the modal
    })

# Attachments page with tabs
@login_required
def attachments_page(request):
    """Attachments page with bot-filtered medicines"""
    workspace = request.user.workspace
    selected_bot = request.selected_bot
    active_tab = request.GET.get("tab", "general")

    # General attachments
    attachments_qs = Attachment.objects.filter(owner=request.user, type="GENERAL").order_by("-created_at")

    # Medicines - FILTER BY BOT
    if selected_bot:
        medicines_qs = Medicine.objects.filter(bot=selected_bot).select_related("category").order_by("-id")
    else:
        medicines_qs = Medicine.objects.none()

    # Search
    q = request.GET.get("q", "").strip()
    if q:
        medicines_qs = medicines_qs.filter(
            Q(name__icontains=q) | Q(brand__icontains=q) | Q(generic_name__icontains=q)
        )

    # Pagination
    paginator = Paginator(medicines_qs, 12)
    page_number = request.GET.get("page", 1)
    medicines_page = paginator.get_page(page_number)

    context = {
        "attachments": attachments_qs,
        "medicines": medicines_page,
        "q": q,
        "workspace": workspace,
        "form": MedicineForm(),
        "active_tab": active_tab,
    }
    return render(request, "owner/attachments/attachments_page.html", context)
@login_required
def medicines_autocomplete(request):
    """
    ترجع JSON لخاصية الـ autocomplete (jQuery UI).
    """
    workspace = _get_request_workspace(request)
    term = request.GET.get("term", "").strip()
    results = []
    if term:
        qs = Medicine.objects.filter(
            Q(name__icontains=term) |
            Q(sku__icontains=term) |
            Q(brand__icontains=term)
        )
        if workspace:
            qs = qs.filter(workspace=workspace)
        meds = qs.values("id", "name", "sku")[:10]
        results = [
            {"id": m["id"], "label": f'{m["name"]} ({m["sku"]})', "value": m["name"]}
            for m in meds
        ]
    return JsonResponse(results, safe=False)
# -----------------------


@login_required
@require_POST
def update_stock(request, pk):
    """
    تحديث المخزون لدواء واحد (inline). يُعيد HTML للصف بعد التحديث.
    """
    med = get_object_or_404(Medicine, pk=pk)
    # تحقق أن المستخدم يعمل على نفس مساحة العمل (إن لزم)
    workspace = _get_request_workspace(request)
    if workspace and med.workspace_id != workspace.id:
        return HttpResponseForbidden("Not authorized for this medicine")

    try:
        new_stock = int(request.POST.get("stock"))
    except (TypeError, ValueError):
        return HttpResponseBadRequest("Invalid stock value")

    med.stock_quantity = new_stock
    med.save(update_fields=["stock_quantity"])

    # نرجع صف HTML ليتم استبداله في الواجهة (AJAX)
    html = render_to_string("owner/medicines/_medicine_row.html", {"m": med}, request=request)
    return JsonResponse({"html": html})


@login_required
def export_medicines_csv(request):
    """
    تصدير كل الأدوية (تابع لمساحة العمل إن كانت موجودة) كـ CSV.
    """
    workspace = _get_request_workspace(request)
    qs = Medicine.objects.all().order_by("name")
    if workspace:
        qs = qs.filter(workspace=workspace)

    response = HttpResponse(content_type="text/csv")
    filename = f"medicines_{workspace.name if workspace else 'all'}.csv"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow(["sku", "name", "brand", "generic_name", "price", "currency", "stock_quantity", "low_stock_threshold"])

    for m in qs:
        writer.writerow([
            m.sku or "",
            m.name or "",
            m.brand or "",
            m.generic_name or "",
            str(m.price) if m.price is not None else "",
            m.currency or "",
            str(m.stock_quantity),
            str(m.low_stock_threshold),
        ])

    return response

# map CSV import
# خريطة أسماء الحقول المحتملة
FIELD_MAP = {
    "sku": ["sku", "SKU", "product_code", "item_code"],
    "name": ["name", "Name", "product_name", "medicine_name"],
    "brand": ["brand", "Brand", "manufacturer"],
    "generic_name": ["generic_name", "Generic", "gen_name"],
    "price": ["price", "Price", "cost", "unit_price"],
    "currency": ["currency", "Currency"],
    "stock_quantity": ["stock_quantity", "stock", "qty", "quantity"],
    "low_stock_threshold": ["low_stock_threshold", "min_stock", "threshold"],
}


# جميع الحقول الممكنة من الموديل (وسعنا القائمة)
MODEL_FIELDS = [
    "sku", "name", "brand", "generic_name",
    "strength", "dosage_form", "price", "currency",
    "stock_quantity", "low_stock_threshold"
]
def validate_value_for_field(field, val):
    """يتحقق أن القيمة تناسب الحقل، وإلا يتجاهلها."""
    if not val:
        return None
    val = val.strip()
    try:
        if field in ["stock_quantity", "low_stock_threshold"]:
            return int(float(val))
        elif field == "price":
            return float(val.replace(",", ""))
        elif field == "sku":
            return val if len(val) <= 20 else None
        elif field in ["strength", "dosage_form", "brand", "generic_name", "name", "currency"]:
            return val  # نصوص مسموح بها
        else:
            return val
    except:
        return None

# 
@login_required
@require_POST
def medicine_import_upload(request):
    """Handle file upload and extract column headers for mapping."""
    import pandas as pd
    
    upload_file = request.FILES.get('import_file')
    if not upload_file:
        return JsonResponse({'success': False, 'error': 'No file uploaded'}, status=400)
    
    try:
        # Check file extension
        file_ext = upload_file.name.split('.')[-1].lower()
        
        # Read file using pandas
        if file_ext in ['xlsx', 'xls']:
            df = pd.read_excel(upload_file)
        elif file_ext == 'csv':
            df = pd.read_csv(upload_file)
        else:
            return JsonResponse({'success': False, 'error': 'Unsupported file format. Use Excel (.xlsx, .xls) or CSV.'}, status=400)
        
        # Store file data in session
        request.session['import_data'] = df.to_json(orient='split')
        request.session['import_filename'] = upload_file.name
        
        # Get column headers and sample data
        columns_info = []
        for col in df.columns:
            sample_values = df[col].head(3).fillna('').tolist()
            data_type = str(df[col].dtype)
            columns_info.append({
                'name': col,
                'sample': sample_values,
                'type': data_type
            })
        
        # Available database fields
        db_fields = [
            {'value': '', 'label': '-- Skip --'},
            {'value': 'name', 'label': 'Medicine Name *', 'required': True},
            {'value': 'sku', 'label': 'SKU/Code'},
            {'value': 'generic_name', 'label': 'Generic Name'},
            {'value': 'brand', 'label': 'Brand'},
            {'value': 'category', 'label': 'Category'},
            {'value': 'price', 'label': 'Price *', 'required': True},
            {'value': 'stock_quantity', 'label': 'Stock Quantity *', 'required': True},
            {'value': 'low_stock_threshold', 'label': 'Low Stock Threshold'},
            {'value': 'dosage_form', 'label': 'Dosage Form'},
            {'value': 'strength', 'label': 'Strength'},
            {'value': 'description', 'label': 'Description'},
        ]
        
        return JsonResponse({
            'success': True,
            'columns': columns_info,
            'db_fields': db_fields,
            'total_rows': len(df)
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_POST
def medicine_import_preview(request):
    """Preview file contents with column mapping applied."""
    import pandas as pd
    import json
    
    # Get stored data
    import_data_json = request.session.get('import_data')
    if not import_data_json:
        return JsonResponse({'success': False, 'error': 'No import data found. Please upload file again.'}, status=400)
    
    try:
        # Parse mapping from request
        mapping = json.loads(request.POST.get('mapping', '{}'))
        
        # Reconstruct dataframe
        df = pd.read_json(import_data_json, orient='split')
        
        # Apply column mapping and show preview (first 50 rows)
        preview_data = []
        for idx, row in df.head(50).iterrows():
            mapped_row = {'_row_num': idx + 1}
            for file_col, db_field in mapping.items():
                if db_field and file_col in df.columns:
                    mapped_row[db_field] = str(row[file_col]) if pd.notna(row[file_col]) else ''
            preview_data.append(mapped_row)
        
        # Get unique mapped fields for column headers
        mapped_fields = set(mapping.values()) - {''}
        
        return JsonResponse({
            'success': True,
            'preview_data': preview_data,
            'mapped_fields': list(mapped_fields),
            'total_rows': len(df)
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)



def guess_column_type(values):
    """تخمين نوع العمود من القيم."""
    clean = [v.strip() for v in values if v and v.strip()]
    if not clean:
        return None
    sample = clean[:20]

    if all(re.match(r"^[A-Za-z0-9\-_]+$", v) and len(v) <= 15 for v in sample):
        return "sku"
    if all(v.isdigit() for v in sample):
        return "stock_quantity"
    if all(re.match(r"^\d+(\.\d+)?$", v) for v in sample):
        return "price"
    if all(len(v) <= 4 and v.isalpha() for v in sample):
        return "currency"

    avg_len = sum(len(v) for v in sample) / len(sample)
    if avg_len > 10:
        return "name"
    elif avg_len > 5:
        return "brand"
    else:
        return "generic_name"


@login_required
@require_POST
def medicine_import_process(request):
    """Process import with column mapping and data type conversion."""
    import pandas as pd
    import json
    from decimal import Decimal, InvalidOperation
    
    # Get stored data
    import_data_json = request.session.get('import_data')
    if not import_data_json:
        return JsonResponse({'success': False, 'error': 'No import data found. Please upload file again.'}, status=400)
    
    try:
        # Parse mapping from request
        mapping = json.loads(request.POST.get('mapping', '{}'))
        
        # Validate required fields are mapped
        required_fields = ['name', 'price', 'stock_quantity']
        mapped_db_fields = set(mapping.values()) - {''}
        missing_required = [f for f in required_fields if f not in mapped_db_fields]
        
        if missing_required:
            return JsonResponse({
                'success': False,
                'error': f'Required fields not mapped: {", ".join(missing_required)}'
            }, status=400)
        
        # Reconstruct dataframe
        df = pd.read_json(import_data_json, orient='split')
        
        # Get workspace
        workspace = _get_request_workspace(request)
        if not workspace:
            return JsonResponse({'success': False, 'error': 'No workspace found for current user'}, status=400)
        
        # Process each row
        created_count = 0
        updated_count = 0
        skipped_count = 0
        errors = []
        
        for idx, row in df.iterrows():
            try:
                medicine_data = {'workspace': workspace}
                
                # Apply column mapping with data type conversion
                for file_col, db_field in mapping.items():
                    if not db_field or file_col not in df.columns:
                        continue
                    
                    raw_value = row[file_col]
                    
                    # Skip empty values
                    if pd.isna(raw_value) or str(raw_value).strip() == '':
                        continue
                    
                    # Data type conversion based on field
                    try:
                        if db_field == 'price':
                            # Convert string to decimal, handle currency symbols
                            price_str = str(raw_value).replace('$', '').replace(',', '').strip()
                            medicine_data['price'] = Decimal(price_str)
                            
                        elif db_field in ['stock_quantity', 'low_stock_threshold']:
                            # Convert to integer
                            medicine_data[db_field] = int(float(str(raw_value)))
                            
                        elif db_field == 'category':
                            # Match or create category
                            category_name = str(raw_value).strip()
                            category, _ = Category.objects.get_or_create(
                                name__iexact=category_name,
                                workspace=workspace,
                                defaults={'name': category_name}
                            )
                            medicine_data['category'] = category
                            
                        else:
                            # String fields - direct assignment with truncation if needed
                            value_str = str(raw_value).strip()
                            # Check max_length for CharField
                            field_obj = Medicine._meta.get_field(db_field)
                            if hasattr(field_obj, 'max_length') and field_obj.max_length:
                                value_str = value_str[:field_obj.max_length]
                            medicine_data[db_field] = value_str
                            
                    except (ValueError, InvalidOperation, TypeError) as e:
                        # Skip this field if conversion fails
                        errors.append(f'Row {idx + 1}: Could not convert "{raw_value}" to {db_field} - {str(e)}')
                        continue
                
                # Validate required fields
                if 'name' not in medicine_data:
                    skipped_count += 1
                    errors.append(f'Row {idx + 1}: Missing required field "name"')
                    continue
                
                # Create or update medicine
                sku = medicine_data.get('sku')
                if sku:
                    # Update existing or create new based on SKU
                    medicine, created = Medicine.objects.update_or_create(
                        sku=sku,
                        workspace=workspace,
                        defaults=medicine_data
                    )
                else:
                    # Create new without SKU
                    medicine = Medicine.objects.create(**medicine_data)
                    created = True
                
                if created:
                    created_count += 1
                else:
                    updated_count += 1
                    
            except Exception as e:
                skipped_count += 1
                errors.append(f'Row {idx + 1}: {str(e)}')
                continue
        
        # Clear session data
        if 'import_data' in request.session:
            del request.session['import_data']
        if 'import_filename' in request.session:
            del request.session['import_filename']
        
        return JsonResponse({
            'success': True,
            'created': created_count,
            'updated': updated_count,
            'skipped': skipped_count,
            'total_processed': created_count + updated_count,
            'errors': errors[:10]  # Return first 10 errors only
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    


# ////////////////////////////////////////////////////////////////

# # medicine add
# @owner_required
# def medicine_add(request):
#     pharmacy = request.pharmacy
#     if request.method == "POST":
#         form = MedicineForm(request.POST, request.FILES)
#         if form.is_valid():
#             med = form.save(commit=False)
#             med.pharmacy = pharmacy

#             uploaded_file = request.POST.get("uploaded_file", "").strip()  # filename returned by FilePond
#             # If uploading via FilePond: move from temp -> medicines
#             if uploaded_file:
#                 temp_path = os.path.join(settings.MEDIA_ROOT, "temp", uploaded_file)
#                 if os.path.exists(temp_path):
#                     final_dir = os.path.join(settings.MEDIA_ROOT, "medicines")
#                     os.makedirs(final_dir, exist_ok=True)
#                     final_path = os.path.join(final_dir, uploaded_file)
#                     shutil.move(temp_path, final_path)
#                     med.image.name = f"medicines/{uploaded_file}"
#                 else:
#                     # maybe client posted a final path already (unlikely on add)
#                     med.image.name = uploaded_file

#             # Save model
#             med.save()
#             messages.success(request, "Medicine added.")
#             return redirect("pharmacy_app:medicines_list")
#     else:
#         form = MedicineForm()

#     # prefill uploaded_file hidden input empty for add
#     return render(request, "owner/medicine_form.html", {"form": form})


# # medicine edit
# @owner_required
# def medicine_edit(request, pk):
#     pharmacy = request.pharmacy
#     med = get_object_or_404(Medicine, pk=pk, pharmacy=pharmacy, bot=request.selected_bot)  # Verify bot ownership

#     if request.method == "POST":
#         form = MedicineForm(request.POST, request.FILES, instance=med)
#         if form.is_valid():
#             med = form.save(commit=False)

#             uploaded_file = request.POST.get("uploaded_file", "").strip()

#             if uploaded_file:
#                 # if uploaded_file equals existing final name (e.g. 'medicines/xyz.jpg')
#                 # then nothing to move; if it's a temp file name, move it.
#                 temp_path = os.path.join(settings.MEDIA_ROOT, "temp", uploaded_file)
#                 if os.path.exists(temp_path):
#                     final_dir = os.path.join(settings.MEDIA_ROOT, "medicines")
#                     os.makedirs(final_dir, exist_ok=True)
#                     final_path = os.path.join(final_dir, uploaded_file)
#                     # remove old image file (optional) if you want
#                     if med.image:
#                         try:
#                             old = os.path.join(settings.MEDIA_ROOT, med.image.name)
#                             if os.path.exists(old) and not old.endswith(uploaded_file):
#                                 os.remove(old)
#                         except Exception:
#                             pass
#                     shutil.move(temp_path, final_path)
#                     med.image.name = f"medicines/{uploaded_file}"
#                 else:
#                     # value might be final already (e.g. 'medicines/xyz.jpg')
#                     # if it contains '/', use as is
#                     if "/" in uploaded_file:
#                         med.image.name = uploaded_file
#                     else:
#                         # fallback: leave unchanged
#                         pass

#             med.save()
#             messages.success(request, "Medicine updated.")
#             return redirect("pharmacy_app:medicines_list")
#     else:
#         form = MedicineForm(instance=med)

#     # pass existing image name so template can set hidden field initial value
#     return render(request, "owner/medicine_form.html", {
#         "form": form,
#         "existing_image_name": med.image.name if med.image else "",
#         "existing_image_url": med.image.url if med.image else ""
#     })

def _move_temp_to_final(temp_filename, medicine_instance):
    """Move a temp file into media/medicines and set medicine_instance.image"""
    temp_path = os.path.join(settings.MEDIA_ROOT, "temp", temp_filename)
    if not os.path.exists(temp_path):
        return False
    final_dir = os.path.join(settings.MEDIA_ROOT, "medicines")
    os.makedirs(final_dir, exist_ok=True)
    final_path = os.path.join(final_dir, temp_filename)
    # remove any existing file with same name
    if os.path.exists(final_path):
        os.remove(final_path)
    shutil.move(temp_path, final_path)
    # set Django ImageField name (relative to MEDIA_ROOT)
    medicine_instance.image.name = f"medicines/{temp_filename}"
    return True

@owner_required
def medicine_add(request):
    workspace = request.workspace
    if request.method == "POST":
        form = MedicineForm(request.POST, request.FILES)
        if form.is_valid():
            med = form.save(commit=False)
            med.workspace = workspace
            med.bot = request.selected_bot  # Assign to selected bot
            uploaded_file = request.POST.get("uploaded_file", "").strip()  # may be temp filename or existing
            if uploaded_file:
                # If it contains '/', assume it's already final path (e.g. 'medicines/xxx')
                if "/" in uploaded_file or uploaded_file.startswith("medicines/"):
                    med.image.name = uploaded_file.replace("media/", "").lstrip("/")
                else:
                    _move_temp_to_final(uploaded_file, med)
            med.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({"success": True, "message": "Medicine added successfully"})
                
            messages.success(request, "Medicine added successfully")
            return redirect(f"{reverse('pharmacy_app:attachments_page')}?tab=medicines")
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({"success": False, "errors": form.errors}, status=400)
    else:
        form = MedicineForm()
    return render(request, "owner/medicine_form.html", {"form": form, "existing_image_name": "", "existing_image_url": ""})

@owner_required
def medicine_edit(request, pk):
    workspace = request.workspace
    med = get_object_or_404(Medicine, pk=pk, workspace=workspace, bot=request.selected_bot)  # Verify bot ownership
    existing_name = med.image.name if med.image else ""
    existing_url = med.image.url if med.image else ""
    
    if request.method == "POST":
        form = MedicineForm(request.POST, request.FILES, instance=med)
        if form.is_valid():
            med = form.save(commit=False)
            uploaded_file = request.POST.get("uploaded_file", "").strip()

            if uploaded_file:
                # if uploaded_file is same as existing_name, do nothing
                if uploaded_file != existing_name:
                    # It's a new temp file
                    if "/" in uploaded_file or uploaded_file.startswith("medicines/"):
                         # Already a path? check if temp
                         pass
                    
                    # Move from temp
                    temp_path = os.path.join(settings.MEDIA_ROOT, "temp", uploaded_file)
                    if os.path.exists(temp_path):
                        # Delete old image if exists
                        if med.image:
                            old_path = med.image.path
                            if os.path.exists(old_path):
                                try:
                                    os.remove(old_path)
                                except Exception:
                                    pass
                        
                        with open(temp_path, 'rb') as f:
                            med.image.save(uploaded_file, File(f), save=False)
                        # Remove temp
                        os.remove(temp_path)
            
            med.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({"success": True, "message": "Medicine updated successfully"})

            messages.success(request, "Medicine updated successfully", extra_tags='update')
            return redirect(f"{reverse('pharmacy_app:attachments_page')}?tab=medicines")
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({"success": False, "errors": form.errors}, status=400)
    else:
        form = MedicineForm(instance=med)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string("owner/partials/medicine_form_modal_content.html", {
            "form": form,
            "existing_image_name": existing_name,
            "existing_image_url": existing_url
        }, request=request)
        return JsonResponse({"html": html})

    return render(request, "owner/medicine_form.html", {
        "form": form,
        "existing_image_name": existing_name,
        "existing_image_url": existing_url
    })
@owner_required
def medicine_delete(request, pk):
    workspace = request.workspace
    med = get_object_or_404(Medicine, pk=pk, workspace=workspace, bot=request.selected_bot)  # Verify bot ownership
    if request.method == "POST":
        med.delete()
        messages.success(request, "Medicine deleted successfully")
        return redirect(f"{reverse('pharmacy_app:attachments_page')}?tab=medicines")
    return render(request, "owner/medicine_confirm_delete.html", {"medicine": med})


# -----------------------

# ---------- Temp upload endpoint used by FilePond ----------

@csrf_exempt
def upload_temp_image(request):
    """
    Process (POST) and revert (DELETE) endpoint for FilePond temp uploads.
    - POST: receives file under field "file", writes it to MEDIA_ROOT/temp/, returns plain filename text.
    - DELETE: receives request body text = filename, deletes MEDIA_ROOT/temp/<filename>.
    """
    temp_dir = os.path.join(settings.MEDIA_ROOT, "temp")
    os.makedirs(temp_dir, exist_ok=True)

    if request.method == "POST":
        if "file" not in request.FILES:
            return HttpResponseBadRequest("No file received")
        f = request.FILES["file"]
        orig_name = os.path.splitext(f.name)[0]
        ext = os.path.splitext(f.name)[1] or ""
        safe_base = slugify(orig_name) or "file"
        filename = f"{uuid.uuid4().hex}_{safe_base}{ext}"
        filename = filename.replace('-', '_')
        full_path = os.path.join(temp_dir, filename)
        with open(full_path, "wb+") as dst:
            for chunk in f.chunks():
                dst.write(chunk)
        # Return plain filename (FilePond expects plain text id)
        return HttpResponse(filename, content_type="text/plain")

    elif request.method == "DELETE":
        # FilePond sends the filename (serverId) in the body for revert: delete it
        try:
            file_id = request.body.decode().strip()
        except Exception:
            return HttpResponseBadRequest("Invalid body")
        if not file_id:
            return HttpResponseBadRequest("Empty filename")
        path = os.path.join(temp_dir, file_id)
        try:
            if os.path.exists(path):
                os.remove(path)
                return JsonResponse({"deleted": True})
            else:
                return JsonResponse({"deleted": False, "reason": "not_found"}, status=404)
        except Exception as e:
            return JsonResponse({"deleted": False, "reason": str(e)}, status=500)
    else:
        return HttpResponseBadRequest("Method not allowed")
    

# 

def delete_temp_file(filename):
    from django.conf import settings
    path = os.path.join(settings.MEDIA_ROOT, "temp", filename)
    if os.path.exists(path):
        os.remove(path)
# 

@csrf_exempt
def delete_temp_image(request):
    """
    Accepts POST body containing the temp filename (plain text) and deletes it from MEDIA_ROOT/temp/.
    This endpoint is used by client cancel / beforeunload cleanup (sendBeacon or fetch).
    Returns JSON {deleted: true/false}
    """
    if request.method != "POST":
        return HttpResponseBadRequest("Only POST allowed")

    # try decode raw body first (sendBeacon will send raw text in body)
    filename = ""
    try:
        filename = request.body.decode().strip()
    except Exception:
        filename = ""

    # fallback to form param
    if not filename:
        filename = request.POST.get("filename", "").strip()

    if not filename:
        return JsonResponse({"deleted": False, "reason": "no filename"}, status=400)

    temp_path = os.path.join(settings.MEDIA_ROOT, "temp", filename)
    try:
        if os.path.exists(temp_path):
            os.remove(temp_path)
            return JsonResponse({"deleted": True})
        else:
            return JsonResponse({"deleted": False, "reason": "not found"})
    except Exception as e:
        return JsonResponse({"deleted": False, "reason": str(e)}, status=500)


# /////////////////////////////////////////////////////////////
def handle_uploaded_image(filename, medicine):
    temp_path = os.path.join(settings.MEDIA_ROOT, "temp", filename)
    final_dir = os.path.join(settings.MEDIA_ROOT, "medicines")
    os.makedirs(final_dir, exist_ok=True)
    final_path = os.path.join(final_dir, filename)

    shutil.move(temp_path, final_path)
    medicine.image.name = f"medicines/{filename}"
    medicine.save()



# /////////////////////////////////////////////////////////////
