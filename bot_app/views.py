import re
import json
import requests
from core.models import Workspace, TelegramUser, Attachment
# ecom imports are done lazily inside functions to avoid crashes if tables are missing
from bot_app.models import FAQCategory, FAQ, BotSettings, BotPage
from django.utils.html import escape
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.cache import never_cache
from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.db.models import Prefetch
from django.shortcuts import render, redirect, get_object_or_404
from django import forms
from .forms import BotSettingsForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def _get_request_workspace(request):
    """
    Get the current workspace from the logged-in user or the request parameters.
    """
    # ✅ First priority: from logged-in user's telegram_user link
    if request.user.is_authenticated:
        if hasattr(request.user, 'telegram_user') and getattr(request.user.telegram_user, 'workspace', None):
            return request.user.telegram_user.workspace
        # Optional fallback: if using new `owner` field on Workspace
        if hasattr(request.user, 'workspace'):
            return request.user.workspace
    
    # ✅ Second priority: workspace_id passed explicitly (POST/GET)
    workspace_id = request.POST.get("workspace_id") or request.GET.get("workspace_id") or request.POST.get("pharmacy_id") or request.GET.get("pharmacy_id")
    if workspace_id:
        return Workspace.objects.filter(pk=workspace_id).first()
    return None

@login_required
@never_cache
def bot_manage_view(request):
    selected_bot = request.selected_bot
    if not selected_bot:
        messages.warning(request, "Please create a bot first to manage categories and FAQs.")
        return redirect("bot_app:bot_settings")
    
    # Refresh from DB to ensure we have the latest settings (like home_keyboard_type)
    selected_bot.refresh_from_db()
    
    with open("debug_log.txt", "a", encoding="utf-8") as f:
        f.write(f"DEBUG bot_manage_view: Bot ID {selected_bot.id}, home_keyboard_type={selected_bot.home_keyboard_type}\n")
        
    print(f"DEBUG bot_manage_view: Bot ID {selected_bot.id}, home_keyboard_type={selected_bot.home_keyboard_type}")
    
    workspace = request.user.telegram_user.workspace

    # Get search query
    q = request.GET.get('q', '').strip()
    
    # Filter top categories by bot
    all_top_categories = FAQCategory.objects.filter(
        bot=selected_bot,
        parent__isnull=True
    )
    
    # Apply search filter if query exists
    if q:
        all_top_categories = all_top_categories.filter(name__icontains=q)
    
    all_top_categories = all_top_categories.prefetch_related(
        Prefetch('subcategories', queryset=FAQCategory.objects.prefetch_related('subcategories', 'faqs')),
        'faqs',
    ).order_by('name')

    # Pagination for top-level categories
    per_page = 9
    page = request.GET.get('page', 1)
    paginator = Paginator(all_top_categories, per_page)
    try:
        categories = paginator.page(page)
    except PageNotAnInteger:
        categories = paginator.page(1)
    except EmptyPage:
        categories = paginator.page(paginator.num_pages)

    uncategorized_faqs = FAQ.objects.filter(bot=selected_bot, category__isnull=True
    ).order_by('-created_at')

    context = {
        "categories": categories,
        "uncategorized_faqs": uncategorized_faqs,
        "bot": selected_bot,
        "workspace": workspace,
        "paginator": paginator,
        "q": q,
    }
    return render(request, "bot_app/management/management.html", context)

def faq_list(request):
    workspace = request.user.telegram_user.workspace
    faqs = FAQ.objects.filter(workspace=workspace).order_by('-created_at')
    data = []
    for f in faqs:
        data.append({
            'id': str(f.id),
            'question': f.question,
            'answer': f.answer,
            'category_id': str(f.category.id) if f.category else None,
            'category_name': f.category.name if f.category else '',
            'is_active': f.is_active,
            'created_at': f.created_at.isoformat(),
        })
    return JsonResponse({'success': True, 'data': data})
@require_POST
def faq_create(request):
    workspace = _get_request_workspace(request)
    if not workspace:
        return JsonResponse({'success': False, 'error': 'No workspace context found (login user not linked or workspace_id missing).'}, status=400)
    # Extract form data
    question = (request.POST.get('question') or '').strip()
    answer = (request.POST.get('answer') or '').strip()
    category_id = request.POST.get('category_id') or request.POST.get('category') or None
    is_active_raw = request.POST.get('is_active')
    # 
    print("🧠 Incoming category_id:", category_id)  # ADD THIS LINE
    print("📦 POST data:", request.POST.dict())     # ADD THIS LI
    print("🧩 Received category_id:", category_id)
# 
    # Parse "is_active" safely
    is_active = False
    if isinstance(is_active_raw, str):
        is_active = is_active_raw.lower() in ('on', 'true', '1')
    elif isinstance(is_active_raw, (int, bool)):
        is_active = bool(is_active_raw)
    if not question:
        return JsonResponse({'success': False, 'error': 'Question is required.'}, status=400)
    # Validate category belongs to this workspace
    category = None
    if category_id:
        category = FAQCategory.objects.filter(pk=category_id, workspace=workspace).first()
        if not category:
            # Instead of failing completely, just log it or return explicit error
            return JsonResponse({'success': False, 'error': 'Invalid category (does not belong to your workspace).'}, status=400)
            
    if getattr(request, 'selected_bot', None) is None:
        return JsonResponse({'success': False, 'error': 'No bot selected. Please select a bot first.'}, status=400)
        
    # ✅ Create FAQ tied to correct workspace & category
    faq = FAQ.objects.create(
        bot=request.selected_bot, workspace=workspace,
        category=category,
        question=question,
        answer=answer,
        is_active=is_active
    )
    return JsonResponse({
        'success': True,
        'data': {
            'id': str(faq.id),
            'question': faq.question,
            'answer': faq.answer,
            'category_id': str(category.id) if category else None,
            'category_name': category.name if category else None,
            'is_active': faq.is_active
        }
    })
@require_POST
def faq_update(request, pk):
    faq = get_object_or_404(FAQ, pk=pk)
    faq.question = request.POST.get('question')
    faq.answer = request.POST.get('answer')
    faq.is_active = request.POST.get('is_active') == 'true'
    cat_id = request.POST.get('category_id')
    if cat_id:
        faq.category = get_object_or_404(FAQCategory, pk=cat_id)
    else:
        faq.category = None  # keep uncategorized
    faq.save()
    return JsonResponse({'success': True})
@require_POST
def faq_delete(request, faq_id):
    try:
        faq = FAQ.objects.get(id=faq_id)
        faq.delete()
        return JsonResponse({'success': True})
    except FAQ.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'FAQ not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
# views.py
@login_required
def faq_detail(request, pk):
    """
    Return JSON data for a given FAQ to populate the edit modal
    """
    faq = get_object_or_404(FAQ, pk=pk)
    return JsonResponse({
        'id': str(faq.id),
        'question': faq.question,
        'answer': faq.answer,
        'is_active': faq.is_active,
        'category_id': str(faq.category.id) if faq.category else '',
    })
@require_POST
def toggle_faq_status(request, faq_id):
    try:
        faq = FAQ.objects.get(id=faq_id)
        faq.is_active = not faq.is_active
        faq.save()
        return JsonResponse({'success': True, 'is_active': faq.is_active})
    except FAQ.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'FAQ not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
# --- New Category Views ---
@login_required
def category_list(request):
    workspace = _get_request_workspace(request)
    if not workspace or not request.selected_bot:
        return JsonResponse({"success": False, "data": []})
        
    cats = FAQCategory.objects.filter(bot=request.selected_bot, parent__isnull=True).prefetch_related("subcategories")
    data = []
    for c in cats:
        data.append({
            "id": str(c.id),
            "name": c.name,
            "subcategories": [{"id": str(s.id), "name": s.name} for s in c.subcategories.all()],
        })
    return JsonResponse({"success": True, "data": data})
@login_required
def category_create(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request"})
        
    workspace = _get_request_workspace(request)
    if not workspace or not request.selected_bot:
        return JsonResponse({'success': False, 'error': 'No bot selected or workspace found.'}, status=400)
        
    name = request.POST.get("name", "").strip()
    parent_id = request.POST.get("parent_id")
    parent = FAQCategory.objects.filter(id=parent_id).first() if parent_id else None
    
    if not name:
        return JsonResponse({"success": False, "error": "Name required"})
        
    cat = FAQCategory.objects.create(bot=request.selected_bot, name=name, workspace=workspace, parent=parent)
    return JsonResponse({"success": True, "id": str(cat.id)})
@login_required
def category_update(request, pk):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request"})
    try:
        cat = FAQCategory.objects.get(pk=pk)
    except FAQCategory.DoesNotExist:
        return JsonResponse({"success": False, "error": "Not found"})
    name = request.POST.get("name", "").strip()
    if not name:
        return JsonResponse({"success": False, "error": "Name required"})
    cat.name = name
    cat.save()
    return JsonResponse({"success": True})
@login_required
def category_delete(request, pk):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request"})
    try:
        cat = FAQCategory.objects.get(pk=pk)
    except FAQCategory.DoesNotExist:
        return JsonResponse({"success": False, "error": "Not found"})
        
    # Only enforce workspace check if we can resolve the workspace
    workspace = _get_request_workspace(request)
    if workspace and cat.workspace != workspace:
        return JsonResponse({"success": False, "error": "Permission denied."})
        
    cat.delete()
    return JsonResponse({"success": True})
@login_required
def faq_list_by_category_partial(request, category_id):
    """Return HTML partial with subcategories + faqs + pages for a category (used by AJAX refresh)."""
    try:
        category = get_object_or_404(FAQCategory, pk=category_id)
        faqs = FAQ.objects.filter(category=category, workspace=category.workspace).order_by('-created_at')
        subcats = category.subcategories.all()
        # Prefetch pages and their groups only (M2M tables for attachments/medicines don't exist on production)
        pages = category.pages.prefetch_related('groups').all()
        
        html = render_to_string("bot_app/partials/faq_list_by_category.html", {
            "category": category,
            "faqs": faqs,
            "subcategories": subcats,
            "pages": pages
        }, request=request)
        return JsonResponse({"success": True, "html": html})
    except Exception as e:
        import traceback
        print(f"❌ faq_list_by_category_partial error: {e}")
        print(traceback.format_exc())
        return JsonResponse({"success": False, "error": str(e)}, status=500)

# --- Page & Group Views ---

@login_required
@require_POST
def page_create(request):
    from bot_app.models import BotPage
    category_id = request.POST.get('category_id')
    name = request.POST.get('name', '').strip()
    
    if not name or not category_id:
        return JsonResponse({'success': False, 'error': 'Name and Category ID are required.'})
        
    category = get_object_or_404(FAQCategory, pk=category_id)
    # Ensure category belongs to user's pharmacy/bot context if needed, 
    # but for now assuming login_required + get_object_or_404 is sufficient for basic ownership check 
    # (though ideally we check category.workspace == request.user.telegram_user.workspace)
    
    page = BotPage.objects.create(category=category, name=name)
    return JsonResponse({'success': True, 'id': str(page.id)})

@login_required
@require_POST
def page_update(request, pk):
    from bot_app.models import BotPage
    page = get_object_or_404(BotPage, pk=pk)
    name = request.POST.get('name', '').strip()
    if not name:
        return JsonResponse({'success': False, 'error': 'Name is required.'})
    page.name = name
    page.save()
    return JsonResponse({'success': True})

@login_required
@require_POST
def page_delete(request, pk):
    from bot_app.models import BotPage
    page = get_object_or_404(BotPage, pk=pk)
    page.delete()
    return JsonResponse({'success': True})

@login_required
@require_POST
def group_create(request):
    from bot_app.models import PageGroup, GroupItem
    page_id = request.POST.get('page_id')
    name = request.POST.get('name', '').strip()
    image = request.FILES.get('image')
    
    if not name or not page_id:
        return JsonResponse({'success': False, 'error': 'Name and Page ID are required.'})
        
    page = get_object_or_404(BotPage, pk=page_id)
    
    try:
        contact_bot_username = request.POST.get('contact_bot_username', '').strip()
        group = PageGroup.objects.create(
            page=page, 
            name=name, 
            image=image,
            contact_bot_username=contact_bot_username
        )
        
        # Save items as GroupItem records (replaces broken M2M approach)
        item_names = request.POST.getlist('item_names[]')
        item_descriptions = request.POST.getlist('item_descriptions[]')
        item_images = request.FILES.getlist('item_images[]')
        
        for i, item_name in enumerate(item_names):
            item_name = item_name.strip()
            if not item_name:
                continue
            item_image = item_images[i] if i < len(item_images) else None
            item_desc = item_descriptions[i] if i < len(item_descriptions) else ''
            GroupItem.objects.create(
                group=group,
                name=item_name,
                description=item_desc,
                image=item_image,
                order=i
            )
            
        return JsonResponse({'success': True, 'id': str(group.id)})
    except Exception as e:
        import traceback
        print(f"Error creating group: {e}")
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_POST
def group_delete(request, pk):
    from bot_app.models import PageGroup
    group = get_object_or_404(PageGroup, pk=pk)
    group.delete()
    return JsonResponse({'success': True})

@login_required
def group_detail(request, pk):
    """Fetch group details for editing"""
    from bot_app.models import PageGroup, GroupItem
    group = get_object_or_404(PageGroup, pk=pk)
    items = GroupItem.objects.filter(group=group).order_by('order', 'created_at')
    
    return JsonResponse({
        'success': True,
        'id': str(group.id),
        'name': group.name,
        'contact_bot_username': group.contact_bot_username or '',
        'image_url': group.image.url if group.image else '',
        'items': [
            {
                'id': str(item.id),
                'name': item.name,
                'description': item.description,
                'image_url': item.image.url if item.image else '',
                'order': item.order,
            }
            for item in items
        ]
    })

@login_required
@require_POST
def group_update(request, pk):
    from bot_app.models import PageGroup, GroupItem
    group = get_object_or_404(PageGroup, pk=pk)
    
    try:
        name = request.POST.get('name', '').strip()
        image = request.FILES.get('image')
        
        if not name:
            return JsonResponse({'success': False, 'error': 'Name is required.'})
            
        group.name = name
        group.contact_bot_username = request.POST.get('contact_bot_username', '').strip()
        if image:
            group.image = image
        group.save()
        
        # Sync items: delete old ones and recreate from submitted data
        item_names = request.POST.getlist('item_names[]')
        item_descriptions = request.POST.getlist('item_descriptions[]')
        item_images = request.FILES.getlist('item_images[]')
        
        # Only reset if items were explicitly submitted
        if item_names:
            group.items.all().delete()
            for i, item_name in enumerate(item_names):
                item_name = item_name.strip()
                if not item_name:
                    continue
                item_image = item_images[i] if i < len(item_images) else None
                item_desc = item_descriptions[i] if i < len(item_descriptions) else ''
                GroupItem.objects.create(
                    group=group,
                    name=item_name,
                    description=item_desc,
                    image=item_image,
                    order=i
                )
            
        return JsonResponse({'success': True})
    except Exception as e:
        import traceback
        print(f"Error updating group: {e}")
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def get_attachments(request):
    """Fetch attachments for selection modal"""
    page_id = request.GET.get('page_id')
    bot_id = request.GET.get('bot_id')
    
    # General attachments (files) - Filter by owner
    general_atts = Attachment.objects.filter(owner=request.user, type='GENERAL').order_by('-created_at')
    
    # Medicines (products) - wrapped in try/except in case ecom_medicine table doesn't exist
    medicine_list = []
    try:
        from ecom.models import Medicine
        if bot_id:
            medicine_list = Medicine.objects.filter(bot_id=bot_id).order_by('name')
        elif page_id:
            try:
                page = BotPage.objects.get(id=page_id)
                if page.category and page.category.bot:
                    medicine_list = Medicine.objects.filter(bot=page.category.bot).order_by('name')
            except (BotPage.DoesNotExist, ValueError):
                pass
    except Exception:
        # Medicine table may not exist on all environments - safely return empty list
        medicine_list = []

    def serialize_att(a):
        return {
            'id': str(a.id),
            'title': a.title,
            'description': a.description,
            'file_url': a.image.url if a.image else '',
            'created_at': a.created_at.strftime('%Y-%m-%d')
        }

    def serialize_med(m):
        return {
            'id': str(m.id),
            'title': m.name,
            'description': m.description or '',
            'file_url': m.image.url if m.image else '',
            'created_at': ''
        }

    return JsonResponse({
        'success': True,
        'general': [serialize_att(a) for a in general_atts],
        'medicines': [serialize_med(m) for m in medicine_list]
    })
@login_required
def bot_settings_view(request):
    # Fetch all bots for the user
    bots = BotSettings.objects.filter(owner=request.user).order_by('-created_at')
    # Handle AJAX requests for CRUD
    if request.method == "POST" and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            action = request.POST.get('action')
            if action == 'delete':
                bot_id = request.POST.get('bot_id')
                try:
                    bot = BotSettings.objects.get(id=bot_id, owner=request.user)
                    bot.delete()
                    return JsonResponse({"success": True, "message": "Bot deleted successfully"})
                except BotSettings.DoesNotExist:
                    return JsonResponse({"success": False, "error": "Bot not found"}, status=404)
            elif action == 'save':
                bot_id = request.POST.get('bot_id')
                if bot_id:
                    try:
                        bot = BotSettings.objects.get(id=bot_id, owner=request.user)
                        form = BotSettingsForm(request.POST, instance=bot)
                    except BotSettings.DoesNotExist:
                        return JsonResponse({"success": False, "error": "Bot not found"}, status=404)
                else:
                    bot = BotSettings(owner=request.user)
                    form = BotSettingsForm(request.POST, instance=bot)
                if form.is_valid():
                    try:
                        saved_bot = form.save()
                        return JsonResponse({
                            "success": True,
                            "message": "Bot saved successfully",
                            "bot": {
                                "id": str(saved_bot.id),
                                "workspace_name": saved_bot.workspace_name,
                                "bot_username": saved_bot.bot_username,
                                "is_connected": saved_bot.is_connected,
                                "is_active": saved_bot.is_active
                            }
                        })
                    except Exception as e:
                        import traceback
                        traceback.print_exc()
                        return JsonResponse({"success": False, "error": f"Database Error: {str(e)}"}, status=500)
                else:
                    return JsonResponse({"success": False, "errors": form.errors, "error": str(form.errors)}, status=400)
            elif action == 'get':
                pass
            else:
                return JsonResponse({"success": False, "error": f"Unknown action: {action}"}, status=400)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({"success": False, "error": f"Unexpected error: {str(e)}"}, status=500)
    # For GET request (page load), render the list
    return render(request, "bot_app/settings/bot_settings.html", {
        "bots": bots,
        "form": BotSettingsForm() # Empty form for the modal
    })
@login_required
def bot_get_details(request, pk):
    """AJAX endpoint to get bot details for editing"""
    try:
        bot = BotSettings.objects.get(id=pk, owner=request.user)
        data = {
            "id": str(bot.id),
            "workspace_name": bot.workspace_name,
            "telegram_token": bot.telegram_token,
            "bot_username": bot.bot_username,
            "is_active": bot.is_active,
            "welcome_message": bot.welcome_message,
            "fallback_message": bot.fallback_message,
            "start_keywords": bot.start_keywords,
            "working_hours_start": bot.working_hours_start.strftime('%H:%M') if bot.working_hours_start else '',
            "working_hours_end": bot.working_hours_end.strftime('%H:%M') if bot.working_hours_end else '',
            "language": bot.language,
            "show_contact_info": bot.show_contact_info,
            "contact_phone": bot.contact_phone,
            "contact_address": bot.contact_address,
            "google_maps_link": bot.google_maps_link,
            "enable_ai_mode": bot.enable_ai_mode,
            "is_connected": bot.is_connected
        }
        return JsonResponse({"success": True, "data": data})
    except BotSettings.DoesNotExist:
        return JsonResponse({"success": False, "error": "Bot not found"}, status=404)
@require_POST
@login_required
def test_bot_connection(request):
    """
    AJAX endpoint to validate Telegram token. POST expects 'bot_id' param.
    """
    bot_id = request.POST.get("bot_id")
    if not bot_id:
        return JsonResponse({"success": False, "error": "No bot ID provided"}, status=400)
    try:
        bot = BotSettings.objects.get(id=bot_id, owner=request.user)
    except BotSettings.DoesNotExist:
        return JsonResponse({"success": False, "error": "Bot not found"}, status=404)
    if not bot.telegram_token:
        return JsonResponse({"success": False, "error": "No bot token configured"}, status=400)
    # Call Telegram getMe
    api_url = f"https://api.telegram.org/bot{bot.telegram_token}/getMe"
    try:
        resp = requests.get(api_url, timeout=8)
    except requests.RequestException as e:
        return JsonResponse({"success": False, "error": f"Network error: {str(e)}"}, status=502)
    try:
        data = resp.json()
    except ValueError:
        return JsonResponse({"success": False, "error": "Invalid response from Telegram"}, status=502)
    if data.get("ok"):
        result = data.get("result", {})
        username = result.get("username") or result.get("first_name") or str(result)
        return JsonResponse({"success": True, "message": f"Connection successful: @{username}", "username": username})
    else:
        # Telegram returns {"ok": False, "error_code":..., "description": "..."}
        return JsonResponse({"success": False, "error": data.get("description", "Invalid token")}, status=400)
@login_required
@require_POST
def connect_bot(request):
    """Connect a bot by setting webhook and updating connection status"""
    bot_id = request.POST.get("bot_id")
    if not bot_id:
        return JsonResponse({"success": False, "error": "No bot ID provided"}, status=400)
    try:
        bot = BotSettings.objects.get(id=bot_id, owner=request.user)
    except BotSettings.DoesNotExist:
        return JsonResponse({"success": False, "error": "Bot not found"}, status=404)
    if not bot.telegram_token:
        return JsonResponse({"success": False, "error": "No bot token configured"})
    try:
        # Test the bot token first
        # Test the bot token first
        resp = requests.get(f"https://api.telegram.org/bot{bot.telegram_token}/getMe", timeout=5).json()
        if resp.get("ok"):
            username = resp["result"]["username"]
            
            # SET WEBHOOK
            # Use the production domain if in production, otherwise use SITE_DOMAIN env var or request.get_host()
            # Hardcoding production domain for simplicity since we know it deployed there
            domain = "mytelebot.com" 
            webhook_url = f"https://{domain}/telegram-webhook/{bot.telegram_token}"
            
            webhook_resp = requests.get(f"https://api.telegram.org/bot{bot.telegram_token}/setWebhook?url={webhook_url}").json()
            
            if webhook_resp.get("ok"):
                bot.bot_username = username
                bot.is_connected = True
                bot.save(update_fields=["bot_username", "is_connected"])
                return JsonResponse({
                    "success": True, 
                    "message": f"Bot @{username} connected successfully and webhook set!", 
                    "username": username
                })
            else:
                return JsonResponse({
                    "success": False, 
                    "error": f"Failed to set webhook: {webhook_resp.get('description')}"
                })
        else:
            return JsonResponse({"success": False, "error": resp.get("description", "Failed to connect")})
    except Exception as e:
        return JsonResponse({"success": False, "error": f"Connection error: {str(e)}"})
@require_POST
@login_required
def verify_password(request):
    """Check current user password for token visibility"""
    password = request.POST.get("password", "")
    user = authenticate(username=request.user.username, password=password)
    return JsonResponse({"success": bool(user)})  
@require_POST
@login_required
def disconnect_bot(request):
    """Disconnect bot (clear connection status but keep token)"""
    bot_id = request.POST.get("bot_id")
    if not bot_id:
        return JsonResponse({"success": False, "error": "No bot ID provided"}, status=400)
    try:
        bot = BotSettings.objects.get(id=bot_id, owner=request.user)
    except BotSettings.DoesNotExist:
        return JsonResponse({"success": False, "error": "Bot not found"}, status=404)
    bot.is_connected = False
    bot.save(update_fields=["is_connected"])
    return JsonResponse({"success": True, "message": "Bot disconnected successfully"})

@require_POST
@login_required
def update_keyboard_type(request):
    """Update the default keyboard type for the bot"""
    try:
        data = json.loads(request.body)
        keyboard_type = data.get('keyboard_type')
        print(f"DEBUG update_keyboard_type called with: {keyboard_type}")
        
        if keyboard_type not in ['INLINE', 'REPLY']:
            print("ERROR Invalid keyboard type")
            return JsonResponse({"success": False, "error": "Invalid keyboard type"}, status=400)
        
        if not request.selected_bot:
             print("ERROR No bot selected")
             return JsonResponse({"success": False, "error": "No bot selected"}, status=400)

        # Refetch to ensure we have the latest instance and can save
        bot = BotSettings.objects.get(id=request.selected_bot.id)
        bot.home_keyboard_type = keyboard_type
        bot.save()
        
        with open("debug_log.txt", "a", encoding="utf-8") as f:
            f.write(f"SUCCESS Saved keyboard type: {bot.home_keyboard_type} for bot {bot.id}\n")
            
        print(f"SUCCESS Saved keyboard type: {bot.home_keyboard_type} for bot {bot.id}")
        return JsonResponse({"success": True, "keyboard_type": bot.home_keyboard_type})
    except Exception as e:
        with open("debug_log.txt", "a", encoding="utf-8") as f:
            f.write(f"ERROR in update_keyboard_type: {str(e)}\n")
        print(f"ERROR in update_keyboard_type: {str(e)}")
        return JsonResponse({"success": False, "error": str(e)}, status=500)
@login_required
def subscription_view(request):
    """
    Display subscription management page with current plan and upgrade options
    """
    # Get user information
    user = request.user
    # For now, we'll show a basic subscription page
    # In the future, this can be expanded with a Subscription model
    context = {
        'user_name': user.get_full_name() or user.username,
        'user_email': user.email,
        'member_since': user.date_joined.strftime('%B %Y'),
        'current_plan': 'Free',  # Default plan
    }
    return render(request, "bot_app/subscription/subscription.html", context)
@login_required
@require_http_methods(["POST"])
def activate_subscription(request):
    """
    Activate a subscription using an activation code
    """
    import json
    from django.utils import timezone
    from core.models import PlanActivationCode, AuditLog
    try:
        data = json.loads(request.body)
        code = data.get('code', '').strip().upper()
        if not code:
            return JsonResponse({'success': False, 'error': 'Activation code is required'})
        
        # Find the activation code
        try:
            activation_code = PlanActivationCode.objects.get(code=code)
        except PlanActivationCode.DoesNotExist:
            # Log failed attempt (security)
            AuditLog.objects.create(
                actor_type='user',
                actor_id=str(request.user.id),
                action='activation_failed',
                resource_type='activation_code',
                details={'reason': 'invalid_code', 'code_attempt': code[:5] + '...'}, # Mask code
                ip_address=request.META.get('REMOTE_ADDR')
            )
            return JsonResponse({'success': False, 'error': 'Invalid activation code'})
            
        # Check if code is valid
        if activation_code.is_used:
             AuditLog.objects.create(
                actor_type='user',
                actor_id=str(request.user.id),
                action='activation_failed',
                resource_type='activation_code',
                resource_id=str(activation_code.id),
                details={'reason': 'already_used'},
                ip_address=request.META.get('REMOTE_ADDR')
            )
             return JsonResponse({'success': False, 'error': 'This activation code has already been used'})
             
        if activation_code.expires_at and activation_code.expires_at < timezone.now():
             AuditLog.objects.create(
                actor_type='user',
                actor_id=str(request.user.id),
                action='activation_failed',
                resource_type='activation_code',
                resource_id=str(activation_code.id),
                details={'reason': 'expired'},
                ip_address=request.META.get('REMOTE_ADDR')
            )
             return JsonResponse({'success': False, 'error': 'This activation code has expired'})

        # Check user-specific restriction
        if activation_code.code_type == 'user_specific':
             # Ensure request.user is linked to the target telegram user
             if not hasattr(request.user, 'telegram_user') or activation_code.target_user != request.user.telegram_user:
                 AuditLog.objects.create(
                    actor_type='user',
                    actor_id=str(request.user.id),
                    action='activation_failed',
                    resource_type='activation_code',
                    resource_id=str(activation_code.id),
                    details={'reason': 'wrong_user'},
                    ip_address=request.META.get('REMOTE_ADDR')
                )
                 return JsonResponse({'success': False, 'error': 'This code is not valid for your account'})

        # Activate the subscription
        activation_code.is_used = True
        activation_code.used_by = request.user.telegram_user if hasattr(request.user, 'telegram_user') else None
        activation_code.used_at = timezone.now()
        activation_code.save()
        
        # Log success
        AuditLog.objects.create(
            actor_type='user',
            actor_id=str(request.user.id),
            action='activation_success',
            resource_type='activation_code',
            resource_id=str(activation_code.id),
            details={'plan': activation_code.plan_name},
            ip_address=request.META.get('REMOTE_ADDR')
        )

        # Update the user's subscription plan
        # Assuming we update the workspace subscription
        workspace = _get_request_workspace(request)
        if workspace:
            from core.models import Subscription
            
            # Free Trial Logic
            duration_days = 30 # Default
            if activation_code.plan_name == 'Free Trial':
                # Check if already used
                tg_user = request.user.telegram_user
                if tg_user.has_used_free_trial:
                     return JsonResponse({'success': False, 'error': 'You have already used your Free Trial.'})
                
                duration_days = 7
                # Mark as used
                tg_user.has_used_free_trial = True
                tg_user.save()

            # Deactivate old active subscriptions
            Subscription.objects.filter(workspace=workspace, status='active').update(status='cancelled')
            
            # Create new subscription
            Subscription.objects.create(
                workspace=workspace,
                plan_name=activation_code.plan_name,
                status='active',
                start_date=timezone.now(),
                end_date=timezone.now() + timezone.timedelta(days=duration_days)
            )

        return JsonResponse({
            'success': True,
            'message': f'{activation_code.plan_name} plan activated successfully!',
            'plan': activation_code.plan_name
        })
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid request format'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
# @require_POST
# def faq_update(request, pk):
#     pharmacy = _get_request_pharmacy(request)
#     f = get_object_or_404(FAQ, pk=pk, pharmacy=pharmacy, bot=request.selected_bot)
#     form = FAQForm(request.POST, instance=f)
#     if form.is_valid():
#         form.save()
#         return JsonResponse({'success': True})
#     return JsonResponse({'success': False, 'errors': form.errors}, status=400)
# @require_POST
# def faq_delete(request, pk):
#     pharmacy = _get_request_pharmacy(request)
#     f = get_object_or_404(FAQ, pk=pk, pharmacy=pharmacy, bot=request.selected_bot)
#     f.delete()
#     return JsonResponse({'success': True})
# @login_required
# def bot_settings_view(request):
#     """
#     Show settings page (GET) and accept AJAX POST to save settings (returns JSON).
#     Uses the existing BotSettingsForm and the BotSettings model (first() instance).
#     """
#     # Use single shared settings instance — adjust if you want per-pharmacy later.
#     settings_obj = BotSettings.objects.first()  # create if none
#     if not settings_obj:
#         settings_obj = BotSettings.objects.create(
#             pharmacy_name="",
#         )
#     if request.method == "GET":
#         form = BotSettingsForm(instance=settings_obj)
#         return render(request, "bot_app/bot_settings.html", {"form": form, "settings": settings_obj})
#     # POST: accept normal or AJAX form submit and return JSON
#     if request.method == "POST":
#         # If request is AJAX, we return JsonResponse
#         form = BotSettingsForm(request.POST, instance=settings_obj)
#         if form.is_valid():
#             form.save()
#             return JsonResponse({"success": True})
#         # if invalid form, return errors
#         return JsonResponse({"success": False, "errors": form.errors}, status=400)
#     return HttpResponseBadRequest("Invalid method")
# @login_required
# def bot_settings_view(request):
#     settings_obj, _ = BotSettings.objects.get_or_create(owner=request.user)
#     if request.method == "GET":
#         form = BotSettingsForm(instance=settings_obj)
#         return render(request, "bot_app/bot_settings.html", {"form": form, "settings": settings_obj})
#     if request.method == "POST":
#         form = BotSettingsForm(request.POST, instance=settings_obj)
#         if form.is_valid():
#             form.save()
#             return JsonResponse({"success": True, "message": "Settings saved successfully"})
#         else:
#             return JsonResponse({"success": False, "errors": form.errors}, status=400)
#     form = BotSettingsForm(instance=settings_obj)
#     return render(request, "bot_app/bot_settings.html", {"form": form, "settings": settings_obj})
# @login_required
# def test_bot_connection(request):
#     if request.method != "POST":
#         return HttpResponseBadRequest("Invalid method")
#     token = request.POST.get("token", "").strip()
#     if not token:
#         return JsonResponse({"success": False, "error": "Token is required"})
#     try:
#         resp = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=5)
#         data = resp.json()
#         if data.get("ok"):
#             return JsonResponse({"success": True, "result": data["result"]["username"]})
#         else:
#             return JsonResponse({"success": False, "error": data.get("description", "Failed")})
#     except Exception as e:
#         return JsonResponse({"success": False, "error": str(e)})    
# @login_required
# @require_POST
# def connect_bot(request):
#     settings_obj = BotSettings.objects.first()
#     action = request.POST.get("action", "connect")
#     if action == "disconnect":
#         settings_obj.is_connected = False
#         settings_obj.save()
#         return JsonResponse({"success": True, "message": "Disconnected"})
#     # Connect logic
#     token = request.POST.get("token", "").strip()
#     if not token:
#         return JsonResponse({"success": False, "error": "Please enter a bot token first"})
#     try:
#         resp = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=5).json()
#         if resp.get("ok"):
#             # Save token only after user saves form
#             settings_obj.temp_token = token  # temporary storage in memory
#             settings_obj.temp_username = resp["result"]["username"]
#             settings_obj.is_connected = True
#             settings_obj.save(update_fields=["telegram_token", "bot_username", "is_connected"])
#             # Do NOT overwrite settings_obj.telegram_token yet!
#             return JsonResponse({
#                 "success": True,
#                 "username": resp["result"]["username"]
#             })
#         else:
#             return JsonResponse({"success": False, "error": resp.get("description", "Failed")})
#     except Exception as e:
#         return JsonResponse({"success": False, "error": str(e)})
# @login_required
# def verify_password(request):
#     """
#     Used when showing saved token with eye icon. 
#     Expects POST: {'password': 'current_password'}
#     Returns success True/False
#     """
#     if request.method != "POST":
#         return HttpResponseBadRequest("Invalid method")
#     password = request.POST.get("password", "")
#     user = request.user
#     if user.check_password(password):
#         return JsonResponse({"success": True})
#     else:
#         return JsonResponse({"success": False, "error": "Incorrect password"})   
# --------------------------------------------------------------------------------------
# webhook to receive Telegram updates
# @csrf_exempt
# def telegram_webhook(request):
#     wel = ["hi" , "hello" , "hey" , "start","Hi" , "Hello" , "Hey" ,
#             "Start" , "مرحبا" , "مرحبا" , "السلام عليكم" , "أهلا", "اهلا" , "أهلا وسهلا" ,]
#     if request.method != "POST":
#         return JsonResponse({"status": "ok"})
#     try:
#         update = json.loads(request.body)
#         print("📩 Telegram update received:", update)
#     except json.JSONDecodeError:
#         return JsonResponse({"status": "invalid payload"})
#     if "message" in update:
#         chat_id = update["message"]["chat"]["id"]
#         text = update["message"].get("text", "")
#         print("Message text:", text)
#         if text == "/start":
#             send_categories(chat_id)
#         elif text in wel:
#             send_telegram_message(chat_id, "👋 Hello! Welcome to our pharmacy bot. How can we assist you today?")
#             send_categories(chat_id)
#         else:
#             send_telegram_message(chat_id, f"Please use /start to begin. or {wel}")
#     elif "callback_query" in update:
#         chat_id = update["callback_query"]["message"]["chat"]["id"]
#         data = update["callback_query"]["data"]
#         print("Callback data:", data)
#         handle_callback(chat_id, data)
#     return JsonResponse({"ok": True})
# at top of bot_app/views.py
RETURN_TO_TYPING_BUTTON = "↩️ Return to typing"
BACK_TO_CATEGORIES_BUTTON = "⬅️ Back to categories"
WELCOME_MESSAGES = ["hi" , "hello" , "hey" , "start","Hi" , "Hello" , "Hey" ,
            "Start" , "مرحبا" , "مرحبا" , "السلام عليكم" , "أهلا", "اهلا" , "أهلا وسهلا" ,]
# @csrf_exempt
# def telegram_webhook(request):
#     print("🚨 telegram_webhook is running!")
#     """Receive Telegram updates (webhook)"""
#     if request.method != "POST":
#         return JsonResponse({"status": "ok"})
#     try:
#         update = json.loads(request.body)
#         # debug print to server log:
#         print("🚨 telegram_webhook is running!" , update)
#         print("📩 Telegram update received:", update)
#         print("🚨 telegram_webhook is running!" , update)
#     except json.JSONDecodeError:
#         return JsonResponse({"status": "invalid payload"})
#     # 1) Normal messages (text); user hits /start or types text (we only use /start here)
#     if "message" in update:
#         msg = update["message"]
#         chat_id = msg["chat"]["id"]
#         text = msg.get("text", "")
#         if text and text.strip() == "/start":
#             return send_categories_top(chat_id)
#         # If user types other free text, optionally reply or ignore
#         return JsonResponse({"ok": True})
#     if "message" in update:
#         msg = update["message"]
#         chat_id = msg["chat"]["id"]
#         text = msg.get("text", "").strip()
#         if text == "/start":
#             return send_categories_top(chat_id)
#         # detect if text matches a category name
#         category = FAQCategory.objects.filter(name=text).first()
#         if category:
#             # Show FAQs or subcategories for this category
#             return send_category_content(chat_id, category)
#         return JsonResponse({"ok": True})
#     if "message" in update:
#         msg = update["message"]
#         chat_id = msg["chat"]["id"]
#         text = msg.get("text", "").strip()
#         # /start should always show top categories keyboard
#         if text in WELCOME_MESSAGES or text == "/start":
#             return send_categories_top(chat_id)
#         # special: Return to typing -> remove the reply keyboard and send confirmation
#         if text == RETURN_TO_TYPING_BUTTON:
#             send_telegram_message(chat_id, "✅ Returning to normal typing mode...", reply_markup=remove_reply_keyboard())
#             return JsonResponse({"ok": True})
#         # special: Back to top categories (from subcategories)
#         if text == BACK_TO_CATEGORIES_BUTTON:
#             return send_categories_top(chat_id)
#         # Detect if text matches a category name (top-level or subcategory)
#         category = FAQCategory.objects.filter(name=text).first()
#         if category:
#             return send_category_content(chat_id, category)
#         # If the text came from an inline callback answer (we handle separately) or free text fallback
#         # Optionally reply with fallback:
#         # send_telegram_message(chat_id, "Please choose from the provided menu or press ↩️ to return to typing.")
#         return JsonResponse({"ok": True})
#     # 2) callback_query (inline keyboard button press)
#     if "callback_query" in update:
#         cb = update["callback_query"]
#         data = cb.get("data")
#         message = cb.get("message", {})
#         chat_id = message["chat"]["id"]
#         message_id = message["message_id"]
#         # Respond to the callback by editing the original message
#         try:
#             handle_callback_message(update, data)
#         except Exception as exc:
#             print("Error in handle_callback:", exc)
#         # it's polite to answerCallbackQuery — but the API will accept editing without answer
#         return JsonResponse({"ok": True})
#     return JsonResponse({"ok": True})
# @csrf_exempt
# def telegram_webhook(request):
#     print("🚨 telegram_webhook is running!")
#     if request.method != "POST":
#         return JsonResponse({"status": "ok"})
#     try:
#         update = json.loads(request.body)
#         print("📩 Telegram update received:", update)
#     except json.JSONDecodeError:
#         return JsonResponse({"status": "invalid payload"})
#     # ✅ Handle text messages
#     if "message" in update:
#         msg = update["message"]
#         chat_id = msg["chat"]["id"]
#         text = msg.get("text", "").strip()
#         # ✅ Start or greeting
#         if text in WELCOME_MESSAGES or text == "/start":
#             return send_categories_top(chat_id)
#         # ✅ Return to typing (remove keyboard)
#         if text == RETURN_TO_TYPING_BUTTON:
#             send_telegram_message(
#                 chat_id,
#                 "✅ Returning to normal typing mode...",
#                 reply_markup=remove_reply_keyboard()
#             )
#             return JsonResponse({"ok": True})
#         # ✅ Back to top categories
#         if text == BACK_TO_CATEGORIES_BUTTON:
#             context = user_context.get(chat_id)
#             if context and context.get("parent_id"):
#                 # Go back to parent category
#                 parent_category = FAQCategory.objects.filter(id=context["parent_id"]).first()
#                 if parent_category:
#                     return send_category_content(chat_id, parent_category)
#             # If no parent, show top-level categories
#             return send_categories_top(chat_id)
#         # ✅ Check if selected a category
#         category = FAQCategory.objects.filter(name__iexact=text.replace("📂 ", "")).first()
#         if category:
#             return send_category_content(chat_id, category)
#         # ✅ Check if selected a question
#         faq = FAQ.objects.filter(question__iexact=text.replace("❓ ", "")).first()
#         if faq:
#             send_telegram_message(
#                 chat_id,
#                 f"💬 *{faq.question}*\n\n{faq.answer}",
#                 parse_mode="Markdown"
#             )
#             return JsonResponse({"ok": True})
#         # fallback (if text doesn’t match anything)
#         send_telegram_message(chat_id, "⚠️ Please choose from the menu.")
#         return JsonResponse({"ok": True})
#     # ✅ Handle callback queries (inline keyboard responses)
#     if "callback_query" in update:
#         cb = update["callback_query"]
#         data = cb.get("data")
#         message = cb.get("message", {})
#         chat_id = message["chat"]["id"]
#         try:
#             handle_callback_message(update, data)
#         except Exception as exc:
#             print("❌ Error in handle_callback:", exc)
#         return JsonResponse({"ok": True})
#     return JsonResponse({"ok": True})
# /////////////////////////// ////////// ////////////////////////////////////////////////////////////////////
# /////////////////////////// ////////// ////////////////////////////////////////////////////////////////////
# /////////////////////////// ////////// ////////////////////////////////////////////////////////////////////
# /////////////////////////// ////////// ////////////////////////////////////////////////////////////////////
# @csrf_exempt
# def telegram_webhook(request):
#     if request.method != "POST":
#         return JsonResponse({"status": "ok"})
#     try:
#         update = json.loads(request.body)
#     except json.JSONDecodeError:
#         return JsonResponse({"status": "invalid payload"})
#     # ✅ Handle normal messages
#     if "message" in update:
#         msg = update["message"]
#         chat_id = msg["chat"]["id"]
#         text = msg.get("text", "").strip()
#         # --- /start or greeting
#         if text in WELCOME_MESSAGES or text == "/start":
#             return send_categories_top(chat_id)
#         # --- Return to typing
#         if text == RETURN_TO_TYPING_BUTTON:
#             send_telegram_message(chat_id, "✅ Returning to typing mode...", reply_markup=remove_reply_keyboard())
#             return JsonResponse({"ok": True})
#         # --- Back button
#         if text == BACK_TO_CATEGORIES_BUTTON:
#             return handle_back_button(chat_id)
#         # --- Selected a category
#         category = FAQCategory.objects.filter(name__iexact=text.replace("📂 ", "")).first()
#         if category:
#             return send_category_content(chat_id, category)
#         # --- Selected a question
#         faq = FAQ.objects.filter(question__iexact=text.replace("❓ ", "")).first()
#         if faq:
#             send_telegram_message(chat_id, f"💬 *{faq.question}*\n\n{faq.answer}", parse_mode="Markdown")
#             return JsonResponse({"ok": True})
#         # --- Unknown input
#         send_telegram_message(chat_id, "⚠️ Please choose a valid option.")
#         return JsonResponse({"ok": True})
#     return JsonResponse({"ok": True})
# # ======================================================
# # 🌳 CATEGORIES & NAVIGATION
# # ======================================================
# def send_categories_top(chat_id):
#     """Top-level categories"""
#     categories = FAQCategory.objects.filter(parent=None).order_by("name")
#     if not categories.exists():
#         send_telegram_message(chat_id, "No categories available.", reply_markup=remove_reply_keyboard())
#         return JsonResponse({"ok": True})
#     keyboard = [[f"📂 {cat.name}"] for cat in categories]
#     keyboard.append([RETURN_TO_TYPING_BUTTON])
#     reply_markup = {"keyboard": keyboard, "resize_keyboard": True}
#     send_telegram_message(chat_id, "👋 Welcome! Choose a category:", reply_markup=reply_markup)
#     user_context[chat_id] = {"level": "root", "category_id": None, "parent_id": None}
#     return JsonResponse({"ok": True})
# def send_category_content(chat_id, category):
#     """Show subcategories + questions with loading animation."""
#     # ⏳ Show loading
#     loading_msg = send_telegram_message(chat_id, "⏳ Loading...", parse_mode="Markdown")
#     # time.sleep(1.2)  # short delay to let it appear before removing
#     # ⏳ Animated loading with dots (optional) we we have chatting AI 
#     # loading_msg = animate_loading(chat_id)
#     subcategories = FAQCategory.objects.filter(parent=category).order_by("name")
#     faqs = FAQ.objects.filter(category=category).order_by("question")
#     # Store context for proper Back navigation
#     user_context[chat_id] = {
#         "level": "category",
#         "category_id": category.id,
#         "parent_id": category.parent.id if category.parent else None
#     }
#     # Build keyboard
#     keyboard = [[f"📂 {sub.name}"] for sub in subcategories]
#     keyboard += [[f"❓ {q.question}"] for q in faqs]
#     keyboard.append([BACK_TO_CATEGORIES_BUTTON])
#     keyboard.append([RETURN_TO_TYPING_BUTTON])
#     reply_markup = {"keyboard": keyboard, "resize_keyboard": True}
#     # Message text
#     if subcategories.exists() or faqs.exists():
#         text = f"📁 *{category.name}*\nاختر سؤالاً أو قسماً فرعياً 👇"
#     else:
#         text = f"❌ لا توجد أسئلة أو أقسام فرعية ضمن {category.name}."
#     send_telegram_message(chat_id, text, reply_markup=reply_markup, parse_mode="Markdown")
#     # 🗑️ Remove loading message
#     if loading_msg and "result" in loading_msg:
#         delete_message(chat_id, loading_msg["result"]["message_id"])
#     return JsonResponse({"ok": True})
# def handle_back_button(chat_id):
#     """Navigate back using saved context."""
#     context = user_context.get(chat_id)
#     # No context → go to top
#     if not context or not context.get("category_id"):
#         return send_categories_top(chat_id)
#     current_cat = FAQCategory.objects.filter(id=context["category_id"]).first()
#     if not current_cat:
#         return send_categories_top(chat_id)
#     parent_id = context.get("parent_id")
#     if parent_id:
#         parent_category = FAQCategory.objects.filter(id=parent_id).first()
#         if parent_category:
#             return send_category_content(chat_id, parent_category)
#     # Otherwise → top level
#     return send_categories_top(chat_id)
# ////////////////////////////////////////////////////////////////////////////////////
# ////////////////////////////////////////////////////////////////////////////////////
# ////////////////////////////////////////////////////////////////////////////////////
# ////////////////////////////////////////////////////////////////////////////////////
# ////////////////////////////////////////////////////////////////////////////////////
# def send_categories_top(chat_id):
#     """Send top-level categories as an inline keyboard (new message)."""
#     categories = FAQCategory.objects.filter(parent=None).order_by("name")
#     if not categories.exists():
#         send_telegram_message(chat_id, "No categories configured.")
#         return JsonResponse({"ok": True})
#     keyboard = build_category_inline_keyboard(categories)
#     # 👇 remove the regular keyboard so user only sees inline
#     reply_markup = {
#         "inline_keyboard": keyboard["inline_keyboard"]
#     }
#     # send welcome message with inline only
#     send_telegram_message(
#         chat_id,
#         "👋 Welcome! Please choose a category:",
#         reply_markup=reply_markup
#     )
#     return JsonResponse({"ok": True})
# ---------- down code version with reply keyboard 10 28 2025 -----------------
# def send_categories_top(chat_id):
#     """Send top-level categories as a reply keyboard (replaces typing area)."""
#     categories = FAQCategory.objects.filter(parent=None).order_by("name")
#     if not categories.exists():
#         # still remove keyboard if nothing configured
#         send_telegram_message(chat_id, "No categories configured.", reply_markup=remove_reply_keyboard())
#         return JsonResponse({"ok": True})
#     # Build reply keyboard: list of rows; each row is a list with a single label (you can group multiple per row if desired)
#     keyboard = []
#     for cat in categories:
#         # use plain strings for reply keyboard entries
#         keyboard.append([cat.name])
#     # add a Back/Return row at bottom
#     keyboard.append([RETURN_TO_TYPING_BUTTON])
#     reply_markup = {
#         "keyboard": keyboard,
#         "resize_keyboard": True,
#         "one_time_keyboard": False
#     }
#     # 
#     # 
#     # Send the welcome message with the reply keyboard in place (this replaces the system keyboard)
#     send_telegram_message(
#         chat_id,
#         "👋👋👋👋 any thing Welcome! Please choose a category:",
#         reply_markup=reply_markup
#     )
#     return JsonResponse({"ok": True})
# def send_subcategories_reply(chat_id, parent_category):
#     """Indicate bot is typing."""
#     loading_msg = send_loading_message(chat_id)
#     # send_telegram_chat_action(chat_id, "typing")
#     text = ""
#     """Send subcategories for a parent category as reply keyboard (with back + return)."""
#     subcats = FAQCategory.objects.filter(parent=parent_category).order_by("name")
#     if not subcats.exists():
#         # No subcategories — nothing to show (caller should handle faqs)
#         # return None
#         text = f"❌ لا توجد أسئلة أو أقسام فرعية ضمن {parent_category.name}."
#         return JsonResponse({"ok": True})
#     keyboard = []
#     for sc in subcats:
#         keyboard.append([sc.name])
#     # Back to top categories and Return to typing
#     keyboard.append([BACK_TO_CATEGORIES_BUTTON])
#     keyboard.append([RETURN_TO_TYPING_BUTTON])
#     reply_markup = {
#         "keyboard": keyboard,
#         "resize_keyboard": True,
#         "one_time_keyboard": False
#     }
# # 
# # 
#     if not subcats.exists():
#         send_telegram_message(chat_id, text, reply_markup=reply_markup)
#     else:
#         # 🟨 Message text (header)
#         text = f"📂 *{parent_category.name}*\nاختر سؤالاً أو قسماً فرعياً 👇"
#         send_telegram_message(chat_id, text, reply_markup=reply_markup, parse_mode="Markdown")
#     if loading_msg:
#         delete_message(chat_id, loading_msg["result"]["message_id"])
#     # send_telegram_message(chat_id, f"📂 {parent_category.name} — choose a subcategory:", reply_markup=reply_markup)
#     return JsonResponse({"ok": True})
# def send_category_content(chat_id, category):
#     """Send subcategories + questions under this category."""
#     # 1️⃣ Show loading message first
#     loading_msg = send_loading_message(chat_id)
#     subcategories = FAQCategory.objects.filter(parent=category)
#     faqs = FAQ.objects.filter(category=category)
#    # Store context for Back button
#     user_context[chat_id] = {
#         "level": "category",
#         "category_id": category.id,
#         "parent_id": category.parent.id if category.parent else None  # <-- store parent
#     }
#     buttons = []
#     # 🟦 1. Add subcategories
#     for sub in subcategories:
#         buttons.append(["📂 " + sub.name])
#     # 🟩 2. Add questions
#     for faq in faqs:
#         buttons.append(["❓ " + faq.question])
#     # 🟧 3. Control buttons
#     buttons.append([BACK_TO_CATEGORIES_BUTTON])
#     buttons.append([RETURN_TO_TYPING_BUTTON])
#     reply_markup = {
#         "keyboard": buttons,
#         "resize_keyboard": True,
#         "one_time_keyboard": False,
#     }
#     if not subcategories.exists():
#         # return None
#         return JsonResponse({"ok": True})
#     # 🟨 Message text (header)
#     # if subcategories.exists() or faqs.exists():
#     if subcategories.exists() or faqs.exists():
#         text = f"📁 *{category.name}*\nاختر سؤالاً أو قسماً فرعياً 👇"
#         return send_subcategories_reply(chat_id, category)
#     else:
#         text = f"❌ لا توجد أسئلة أو أقسام فرعية ضمن {category.name}."
#     send_telegram_message(
#         chat_id,
#         text,
#         reply_markup=reply_markup,
#         parse_mode="Markdown"
#     )
#     # Delete loading message
#     # 5️⃣ Delete loading message
#     if loading_msg:
#         delete_message(chat_id, loading_msg["result"]["message_id"])
#     return JsonResponse({"ok": True})
# def send_category_menu(chat_id, category):
#     """
#     Shows both subcategories (top) and questions (bottom) in a single reply keyboard.
#     """
#     subcategories = FAQCategory.objects.filter(parent=category).order_by("name")
#     questions = FAQ.objects.filter(category=category, is_active=True).order_by("question")
#     keyboard = []
#     # --- Header for subcategories ---
#     if subcategories.exists():
#         keyboard.append([f"📂 {category.name} — choose a subcategory:"])
#         for sub in subcategories:
#             keyboard.append([sub.name])
#     # --- Header for questions ---
#     if questions.exists():
#         keyboard.append([f"❓ Questions in {category.name}:"])
#         for q in questions:
#             keyboard.append([q.question])
#     # --- Always add navigation buttons ---
#     keyboard.append([BACK_TO_CATEGORIES_BUTTON])
#     keyboard.append([RETURN_TO_TYPING_BUTTON])
#     reply_markup = {
#         "keyboard": keyboard,
#         "resize_keyboard": True,
#         "one_time_keyboard": False
#     }
#     # Construct message text for context
#     message = f"📁 *{category.name}*\n"
#     if subcategories.exists() and questions.exists():
#         message += "\nSubcategories and questions available 👇"
#     elif subcategories.exists():
#         message += "\nChoose a subcategory 👇"
#     elif questions.exists():
#         message += "\nChoose a question 👇"
#     else:
#         message += "\nNo content available in this category."
#     send_telegram_message(chat_id, message, reply_markup=reply_markup, parse_mode="Markdown")
#     # Save context for Back button
#         if tasks_filter.exists():
#             keyboard = build_task_keyboard(tasks)
#             send_telegram_message(chat_id, f"Tasks in {category.name}:", keyboard)
#             return
#         send_telegram_message(chat_id, "No tasks available in this category.")
#     elif data.startswith("task_"):
#         task_id = data.split("_")[1]
#         send_task_reply(chat_id, task_id)
# code down here not relying on FAQ that stores the actual data but on FAQQuestions
# def handle_callback(chat_id, data):
#     if data.startswith("category_"):
#         cat_id = data.split("_", 1)[1]  # Keep UUID as string
#         category = FAQCategory.objects.get(id=cat_id)
#         subcategories = FAQCategory.objects.filter(parent=category)
#         # questions = FAQQuestion.objects.filter(category=category)
#         questions = FAQ.objects.filter(category=category, is_active=True)
#         # ✅ If both exist
#         if subcategories.exists() and questions.exists():
#             keyboard = []
#             # Section 1 — Subcategories
#             keyboard.append([{"text": "🗃️ Subcategories", "callback_data": "noop"}])
#             for subcat in subcategories:
#                 keyboard.append([{
#                     "text": f"📁 {subcat.name}",
#                     "callback_data": f"category_{subcat.id}"
#                 }])
#             # Divider
#             keyboard.append([{"text": "────────────", "callback_data": "noop"}])
#             # Section 2 — Questions
#             keyboard.append([{"text": "❓ Questions", "callback_data": "noop"}])
#             for q in questions:
#                 keyboard.append([{
#                     "text": f"💬🤔 {q.question[:40]}",
#                     "callback_data": f"task_{q.id}"
#                 }])
#             send_telegram_message(
#                 chat_id,
#                 f"📂 *{category.name}* — Choose what you’d like to explore:",
#                 {"inline_keyboard": keyboard},
#             )
#             return
#         # ✅ If only subcategories exist
#         elif subcategories.exists():
#             keyboard = build_category_keyboard(subcategories)
#             send_telegram_message(
#                 chat_id,
#                 f"🗃️ *{category.name}* — Choose a subcategory:",
#                 keyboard,
#             )
#             return
#         # ✅ If only questions exist
#         elif questions.exists():
#             keyboard = build_task_keyboard(questions)
#             send_telegram_message(
#                 chat_id,
#                 f"💬🤔 *{category.name}* — Available questions:",
#                 keyboard,
#             )
#             return
#         # ✅ If empty
#         else:
#             send_telegram_message(chat_id, "⚠️ No subcategories or questions found here.")
#     elif data.startswith("task_"):
#         task_id = data.split("_", 1)[1]
#         send_task_reply(chat_id, task_id)
#/////// Reply-Keyboard-based navigation handler/////////
# def handle_callback(chat_id, data, message_id=None):
#     if not data:
#         return None
#     # 🏠 Back to Home
#     if data == "back_to_home" or data == "back_to_categories":
#         categories = FAQCategory.objects.filter(parent=None).order_by("name")
#         keyboard = build_category_inline_keyboard(categories)
#         return edit_message_text(chat_id, message_id, "Please choose a category:", reply_markup=keyboard)
# # 
#     if data.startswith("category_"):
#         cat_id = data.split("_", 1)[1]
#         category = FAQCategory.objects.filter(id=cat_id).first()
#         if not category:
#             return edit_message_text(chat_id, message_id, "Category not found.", reply_markup={
#             "inline_keyboard": [[{"text": "🏠 Home", "callback_data": "back_to_home"}]]
#         })
#         subcats = FAQCategory.objects.filter(parent=category).order_by("name")
#         faqs = FAQ.objects.filter(category=category, is_active=True).order_by("question")
#         parent_id = category.parent.id if category.parent else None
#         if subcats.exists():
#             keyboard = build_category_inline_keyboard(subcats, parent_id=parent_id)
#             return edit_message_text(chat_id, message_id, f"📂 {category.name}", reply_markup=keyboard)
#         if faqs.exists():
#             keyboard = build_task_inline_keyboard(faqs, parent_id=parent_id)
#             return edit_message_text(chat_id, message_id, f"❓ {category.name}", reply_markup=keyboard)
#     # return edit_message_text(chat_id, message_id, "⚠️ No content here.", reply_markup={
#     #     "inline_keyboard": [[{"text": "🏠 Home", "callback_data": "back_to_home"}]]
#     # })
# # 
#     # ⬅️ Back to specific parent category
#     if data.startswith("back_to_category_"):
#         parent_id = data.split("_", 3)[-1]
#         parent = FAQCategory.objects.filter(id=parent_id).first()
#         if not parent:
#             return edit_message_text(chat_id, message_id, "Category not found.", reply_markup={
#                 "inline_keyboard": [[{"text": "🏠 Home", "callback_data": "back_to_home"}]]
#             })
#         subcats = FAQCategory.objects.filter(parent=parent).order_by("name")
#         faqs = FAQ.objects.filter(category=parent, is_active=True).order_by("question")
#         # ✅ Correct parent_id reference (use parent.id if nested)
#         parent_parent_id = parent.parent.id if parent.parent else None
#         if subcats.exists():
#             keyboard = build_category_inline_keyboard(subcats, parent_id=parent_parent_id)
#             return edit_message_text(chat_id, message_id, f"📂 {parent.name}", reply_markup=keyboard)
#         if faqs.exists():
#             keyboard = build_task_inline_keyboard(faqs, parent_id=parent_parent_id)
#             return edit_message_text(chat_id, message_id, f"❓ {parent.name}", reply_markup=keyboard)
#         return edit_message_text(chat_id, message_id, "No content here.", reply_markup={
#         "inline_keyboard": [[{"text": "🏠 Home", "callback_data": "back_to_home"}]]
#     })
#     # --- FAQ tapped (show answer) ---
#     if data.startswith("faq_"):
#         faq_id = data.split("_", 1)[1]
#         faq = FAQ.objects.filter(id=faq_id).first()
#         if not faq:
#             return edit_message_text(chat_id, message_id, "Question not found.", reply_markup={
#                 "inline_keyboard": [[{"text": "⬅️ Back", "callback_data": "back_to_categories"}]]
#             })
#         text = f"💬 Q: {faq.question}\n\n🩺 A: {faq.answer or 'No answer provided.'}"
#         # Show Back button that returns to top categories (or you could build 'back to category' to open the category again)
#         markup = {"inline_keyboard": [[{"text": "⬅️ Back", "callback_data": "back_to_categories"}]]}
#         return edit_message_text(chat_id, message_id, text, reply_markup=markup)
#     # default
#     return None
# 3️⃣ Main message handler
# -----------------------------------------
# def handle_callback_message(update, context):
#     chat_id = update.message.chat.id
#     text = update.message.text.strip()
#     # Initialize context
#     if chat_id not in user_context:
#         user_context[chat_id] = {"level": "root", "category_id": None}
#     context.bot.send_chat_action(chat_id=chat_id, action="typing")
#     category = FAQCategory.objects.filter(name__iexact=text.replace("📂 ", "")).first()
#     faq = FAQ.objects.filter(question__iexact=text.replace("❓ ", "")).first()
#     # ---- START / WELCOME ----
#     if text in WELCOME_MESSAGES or text == "/start":
#         categories = FAQCategory.objects.filter(parent__isnull=True)
#         keyboard = [[cat.name] for cat in categories]
#         keyboard.append(["🔚 Return to Normal Mode"])
#         reply_markup = {"keyboard": keyboard, "resize_keyboard": True}
#         send_telegram_message(chat_id, "👋👋👋 Welcome!  in ourChoose a category:", reply_markup=reply_markup)
#         user_context[chat_id] = {"level": "root", "category_id": None}
#         return
#     # ---- RETURN TO NORMAL ----
#     if text == "🔚 Return to Normal Mode":
#         send_telegram_message(chat_id, "Returning to normal mode...", reply_markup={"remove_keyboard": True})
#         user_context[chat_id] = {"level": "root", "category_id": None}
#         return
#     # ---- BACK BUTTON ----
#     # ---- BACK BUTTON ----
#     if text == BACK_TO_CATEGORIES_BUTTON:
#         level = user_context[chat_id]["level"]
#         current_cat_id = user_context[chat_id].get("category_id")
#         if current_cat_id:
#             # Get current category
#             current_category = FAQCategory.objects.filter(id=current_cat_id).first()
#             if not current_category:
#                 # Fallback to top categories
#                 categories = FAQCategory.objects.filter(parent__isnull=True).order_by("name")
#                 keyboard = [[cat.name] for cat in categories]
#                 keyboard.append([RETURN_TO_TYPING_BUTTON])
#                 send_telegram_message(chat_id, "Select a category:", reply_markup={"keyboard": keyboard, "resize_keyboard": True})
#                 user_context[chat_id] = {"level": "root", "category_id": None}
#                 return
#             # Go to parent if exists
#             parent_category = current_category.parent
#             if parent_category:
#                 return send_category_menu(chat_id, parent_category)
#             else:
#                 # Top-level category → show main categories
#                 categories = FAQCategory.objects.filter(parent__isnull=True).order_by("name")
#                 keyboard = [[cat.name] for cat in categories]
#                 keyboard.append([RETURN_TO_TYPING_BUTTON])
#                 send_telegram_message(chat_id, "Select a category:", reply_markup={"keyboard": keyboard, "resize_keyboard": True})
#                 user_context[chat_id] = {"level": "root", "category_id": None}
#                 return
#         # No context → show main categories
#         categories = FAQCategory.objects.filter(parent__isnull=True).order_by("name")
#         keyboard = [[cat.name] for cat in categories]
#         keyboard.append([RETURN_TO_TYPING_BUTTON])
#         send_telegram_message(chat_id, "Select a category:", reply_markup={"keyboard": keyboard, "resize_keyboard": True})
#         user_context[chat_id] = {"level": "root", "category_id": None}
#         return
#     # ---- CATEGORY SELECTED ----
#     category = FAQCategory.objects.filter(name__iexact=text).first()
#     if category:
#         return send_category_menu(chat_id, category)
#     # ---- QUESTION SELECTED ----
#     faq = FAQ.objects.filter(question__iexact=text).first()
#     if faq:
#         send_telegram_message(chat_id, f"💬 *{faq.question}*\n\n{faq.answer}", parse_mode="Markdown")
#         keyboard = [["⬅️ Back"], ["🔚 Return to Normal Mode"]]
#         reply_markup = {"keyboard": keyboard, "resize_keyboard": True}
#         send_telegram_message(chat_id, "You can go back to see other questions.", reply_markup=reply_markup)
#         user_context[chat_id]["level"] = "question"
#         return
#     # ---- UNKNOWN ----
#     send_telegram_message(chat_id, "Please select a valid option from the menu.")
# --------------------------------------------------------------------------------------

@login_required
def debug_errors(request):
    """Secure endpoint to view recent server errors from debug_log.txt"""
    if request.GET.get('token') != 'fixit':
        return JsonResponse({"error": "Unauthorized. Use ?token=fixit"}, status=403)
        
    import os
    log_file = "debug_log.txt"
    if not os.path.exists(log_file):
        return JsonResponse({"status": "No log file found"})
        
    with open(log_file, "r", encoding="utf-8") as f:
        # Get last 200 lines
        lines = f.readlines()[-200:]
        
    return JsonResponse({"logs": lines})

@login_required
def debug_tables(request):
    """View to list all tables in the database to see what's missing"""
    if request.GET.get('token') != 'fixit':
        return JsonResponse({"error": "Unauthorized. Use ?token=fixit"}, status=403)
        
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]
        
    return JsonResponse({"tables": tables, "count": len(tables)})

@login_required
def fix_tables(request):
    """View to attempt forcing the creation of missing tables"""
    if request.GET.get('token') != 'fixit':
        return JsonResponse({"error": "Unauthorized. Use ?token=fixit"}, status=403)
        
    from django.db import connection
    
    results = []
    
    tables_to_create = [
        {
            "name": "bot_group_item",
            "sql": """
            CREATE TABLE IF NOT EXISTS `bot_group_item` (
                `id` char(32) NOT NULL,
                `name` varchar(255) NOT NULL,
                `description` longtext NOT NULL,
                `image` varchar(100) DEFAULT NULL,
                `order` int unsigned NOT NULL DEFAULT 0,
                `created_at` datetime(6) NOT NULL,
                `group_id` char(32) NOT NULL,
                PRIMARY KEY (`id`),
                KEY `bot_group_item_group_id_fk` (`group_id`),
                CONSTRAINT `bot_group_item_group_id_fk` FOREIGN KEY (`group_id`) REFERENCES `bot_page_group` (`id`) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
            """
        }
    ]
    
    with connection.cursor() as cursor:
        for table in tables_to_create:
            try:
                cursor.execute(table["sql"])
                results.append(f"Created table {table['name']} successfully.")
            except Exception as e:
                results.append(f"Table {table['name']}: {e}")
            
    return JsonResponse({
        "success": True, 
        "actions": results
    })
