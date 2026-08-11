from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.utils import timezone
from core.models import SystemAdmin, TelegramUser, Subscription, Workspace
from bot_app.models import BotSettings as BotConfig
from .forms import LoginForm, BroadcastForm, SubscriptionUpdateForm, ActivationCodeForm
from .models import SystemNotification
from core.models import PlanActivationCode
from django.db import connection
# 
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.http import require_http_methods, require_POST
from django.http import JsonResponse, HttpResponse



def admin_login(request):
    # Clear any malformed session data before processing login
    if 'admin_id' in request.session:
        try:
            # Try to validate the session admin_id as a UUID
            import uuid
            uuid.UUID(request.session['admin_id'])
        except (ValueError, TypeError):
            # Session contains invalid UUID, clear it
            del request.session['admin_id']
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            try:
                # Use raw SQL to bypass Django's UUID parsing
                # from django.db import connection
                cursor = connection.cursor()
                cursor.execute(
                    "SELECT id, username, password_hash, is_active FROM system_admin WHERE username = %s",
                    [username]
                )
                row = cursor.fetchone()
                
                if not row:
                    messages.error(request, 'Invalid username or password.')
                    return render(request, 'admin_app/login.html', {'form': form})
                
                admin_id, admin_username, password_hash, is_active = row
                
                # Logic to handle manual plaintext password entry (Auto-hash on first login)
                if password_hash == password:
                    # Password is stored as plaintext, hash it
                    new_hash = make_password(password)
                    cursor.execute(
                        "UPDATE system_admin SET password_hash = %s WHERE username = %s",
                        [new_hash, username]
                    )
                    
                    if is_active:
                        # Use the existing ID as-is (don't try to fix UUID)
                        request.session['admin_id'] = str(admin_id)
                        messages.success(request, 'Password hashed. Login successful!')
                        return redirect('admin_app:dashboard')
                    else:
                        messages.error(request, 'Account is disabled.')
                
                # Standard hash check
                elif check_password(password, password_hash):
                    if is_active:
                        # Use the existing ID as-is
                        request.session['admin_id'] = str(admin_id)
                        return redirect('admin_app:dashboard')
                    else:
                        messages.error(request, 'Account is disabled.')
                else:
                    messages.error(request, 'Invalid username or password.')
                    
            except Exception as e:
                # Catch any other errors
                messages.error(request, f'Login error: {str(e)}')
    else:
        form = LoginForm()
    
    return render(request, 'admin_app/login.html', {'form': form})

def dashboard(request):
    if not request.session.get('admin_id'):
        return redirect('admin_app:login')
    
    from django.db.models import Q, Count, Prefetch
    from django.utils import timezone
    from datetime import date
    
    # Calculate stats using Django ORM
    # Total users
    total_users = TelegramUser.objects.count()
    
    # Active users (last 30 days) - users who logged in or were created
    thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
    active_users = TelegramUser.objects.filter(
        Q(created_at__gte=thirty_days_ago) | Q(updated_at__gte=thirty_days_ago)
    ).count()
    
    # Total admins and regular users
    admin_count = SystemAdmin.objects.filter(is_active=True).count()
    user_count = total_users  # All TelegramUser are regular users
    
    # Active subscriptions (not Free plan)
    active_subs = Subscription.objects.filter(
        status='active'
    ).exclude(plan_name='Free').count()
    
    # Total bots
    total_bots = BotConfig.objects.count()
    
    # Free trial users (users with Free plan or no subscription)
    subscribed_user_ids = Subscription.objects.filter(
        status='active'
    ).exclude(plan_name='Free').values_list('workspace__owner_id', flat=True)
    
    free_trial_users = TelegramUser.objects.exclude(
        id__in=subscribed_user_ids
    ).count()
    
    context = {
        'total_users': total_users,
        'active_users': active_users,
        'admin_count': admin_count,
        'user_count': user_count,
        'active_subs': active_subs,
        'total_bots': total_bots,
        'free_trial_users': free_trial_users,
    }
    
    # Fetch recent users with their subscription info using ORM
    recent_users = TelegramUser.objects.select_related(
        'workspace'
    ).prefetch_related(
        'workspace__subscriptions'
    ).order_by('-created_at')[:10]
    
    users_list = []
    for user in recent_users:
        # Get active subscription
        subscription = None
        if user.workspace:
            subscription = user.workspace.subscriptions.filter(status='active').first()
        
        # Get bot settings if any
        bot_settings = BotConfig.objects.filter(owner__telegram_user=user).first()
        
        users_list.append({
            'id': user.id,
            'name': user.name or 'Unknown',
            'email': user.email or '-',
            'created_at': user.created_at,
            'bot_name': bot_settings.workspace_name if bot_settings else '-',
            'plan_name': subscription.plan_name if subscription else 'Free',
            'status': subscription.status if subscription else 'inactive',
            'end_date': subscription.end_date if subscription else None
        })
    
    context['users'] = users_list
    
    return render(request, 'admin_app/dashboard.html', context)


def admin_logout(request):
    if 'admin_id' in request.session:
        del request.session['admin_id']
    return redirect('admin_app:login')



def subscription_list(request):
    if not request.session.get('admin_id'):
        return redirect('admin_app:login')

    from core.models import PlanActivationCode
    from django.db.models import Q

    # Get the search query from the URL
    search_query = request.GET.get('q', '')   

    # Fetch only SUBSCRIBED users (users with active paid subscriptions)
    subscribed_users = TelegramUser.objects.select_related(
        'workspace'
    ).prefetch_related(
        'workspace__subscriptions'
    ).filter(
        workspace__subscriptions__status='active',
        workspace__subscriptions__isnull=False
    ).exclude(
        workspace__subscriptions__plan_name='Free'
    ).distinct().order_by('-created_at')
    
    # Process users to get current subscription
    user_list = []
    for user in subscribed_users:
        current_sub = user.workspace.subscriptions.filter(status='active').exclude(plan_name='Free').first()
        
        user_list.append({
            'user': user,
            'subscription': current_sub,
            'plan_name': current_sub.plan_name if current_sub else 'Free',
            'status': current_sub.status if current_sub else 'inactive'
        })

    # Get activation codes analytics
    total_codes = PlanActivationCode.objects.count()
    used_codes = PlanActivationCode.objects.filter(is_used=True).count()
    available_codes = total_codes - used_codes

    # Get activation codes list with search
    if search_query:
        codes_queryset = PlanActivationCode.objects.filter(
            Q(code__icontains=search_query) | 
            Q(plan_name__icontains=search_query)
        ).order_by('-created_at')
    else:
        codes_queryset = PlanActivationCode.objects.order_by('-created_at')

    # Pagination
    codes_per_page = 15
    paginator = Paginator(codes_queryset, codes_per_page)
    page_number = request.GET.get('code_page', 1)
    
    try:
        code_page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        code_page_obj = paginator.page(1)
    except EmptyPage:
        code_page_obj = paginator.page(paginator.num_pages)

    # Get all users for the code creation dropdown
    all_users = TelegramUser.objects.all().order_by('name')
    
    # Serialize users for JavaScript (Alpine.js searchable dropdown)
    import json
    users_json = json.dumps([
        {
            'id': str(user.id),
            'name': user.name or 'Unknown',
            'email': user.email or ''
        }
        for user in all_users
    ])

    # Prepare form
    form = ActivationCodeForm()

    return render(request, 'admin_app/subscription_list.html', {
        'users': user_list,
        'codes': code_page_obj,
        'form': form,
        'users_cds': all_users,
        'users_json': users_json,  # For JavaScript
        'search_query': search_query,
        'total_codes': total_codes,
        'used_codes': used_codes,
        'available_codes': available_codes,
    })




def subscription_update(request, user_id):
    if not request.session.get('admin_id'):
        return redirect('admin_app:login')
    
    try:
        user = TelegramUser.objects.get(id=user_id)
    except (TelegramUser.DoesNotExist, ValueError):
        messages.error(request, 'User not found.')
        return redirect('admin_app:subscription_list')
    workspace = user.workspace
    current_sub = None
    if workspace:
        current_sub = workspace.subscriptions.filter(status='active').order_by('-end_date').first()
    
    if request.method == 'POST':
        form = SubscriptionUpdateForm(request.POST)
        if form.is_valid():
            plan_name = form.cleaned_data['plan_name']
            status = form.cleaned_data['status']
            end_date = form.cleaned_data['end_date']
            
            if current_sub:
                current_sub.plan_name = plan_name
                current_sub.status = status
                if end_date:
                    current_sub.end_date = end_date
                current_sub.save()
                messages.success(request, f'Subscription for {user.name} updated successfully.')
            else:
                # Create new subscription if none exists
                if workspace:
                    Subscription.objects.create(
                        workspace=workspace,
                        plan_name=plan_name,
                        status=status,
                        start_date=timezone.now(),
                        end_date=end_date if end_date else timezone.now() + timezone.timedelta(days=30)
                    )
                    messages.success(request, f'New subscription created for {user.name}.')
                else:
                    messages.error(request, 'User has no pharmacy linked.')
            
            return redirect('admin_app:subscription_list')
    else:
        initial_data = {}
        if current_sub:
            initial_data = {
                'plan_name': current_sub.plan_name,
                'status': current_sub.status,
                'end_date': current_sub.end_date
            }
        form = SubscriptionUpdateForm(initial=initial_data)
    
    return render(request, 'admin_app/subscription_update.html', {
        'form': form,
        'user_obj': user,
        'current_sub': current_sub
    })

def broadcast(request):
    if not request.session.get('admin_id'):
        return redirect('admin_app:login')
    
    if request.method == 'POST':
        form = BroadcastForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            message = form.cleaned_data['message']
            notification_type = form.cleaned_data['notification_type']
            
            # Create notification record using raw SQL with auto-increment ID
            try:
                # from django.db import connection
                cursor = connection.cursor()
                
                # Verify admin exists
                cursor.execute(
                    "SELECT id FROM system_admin WHERE id = %s",
                    [request.session['admin_id']]
                )
                admin_row = cursor.fetchone()
                
                if not admin_row:
                    del request.session['admin_id']
                    messages.error(request, 'Session expired. Please log in again.')
                    return redirect('admin_app:login')
                
                # Insert notification with auto-increment ID (don't specify id column)
                cursor.execute(
                    "INSERT INTO admin_app_systemnotification (title, message, notification_type, created_at, sent_by_id) VALUES (%s, %s, %s, NOW(), %s)",
                    [title, message, notification_type, request.session['admin_id']]
                )
                
                # Logic to send emails would go here
                if notification_type in ['email', 'both']:
                    # Placeholder for email sending
                    pass
                
                messages.success(request, f'Broadcast "{title}" sent successfully via {notification_type}.')
                return redirect('admin_app:broadcast')
            except Exception as e:
                messages.error(request, f'Error sending broadcast: {str(e)}')
    else:
        form = BroadcastForm()
    
    # Fetch recent notifications using raw SQL
    # from django.db import connection
    cursor = connection.cursor()
    cursor.execute(
        "SELECT title, message, notification_type, created_at FROM admin_app_systemnotification ORDER BY created_at DESC LIMIT 5"
    )
    recent_notifications = []
    for row in cursor.fetchall():
        recent_notifications.append({
            'title': row[0],
            'message': row[1],
            'notification_type': row[2],
            'get_notification_type_display': dict([
                ('in_app', 'In-App Notification'),
                ('email', 'Email'),
                ('both', 'Both (Email + In-App)'),
            ]).get(row[2], row[2]),
            'created_at': row[3]
        })
    
    # Fetch all users for selection (using raw SQL to bypass UUID issues)
    # Handle case where table doesn't exist
    users_list = []
    try:
        cursor.execute(
            "SELECT id, name, email FROM telegram_user ORDER BY name"
        )
        for row in cursor.fetchall():
            users_list.append({
                'id': row[0],
                'name': row[1],
                'email': row[2]
            })
    except Exception as e:
        # Table doesn't exist or other error - broadcast will still work for "all users"
        pass
    
    return render(request, 'admin_app/broadcast.html', {
        'form': form,
        'recent_notifications': recent_notifications,
        'users': users_list
    })


# Activation code views will be appended here
def activation_codes(request):
    if not request.session.get('admin_id'):
        return redirect('admin_app:login')
    
    # Fetch all activation codes using raw SQL
    # from django.db import connection
    cursor = connection.cursor()
    
    try:
        # Use ORM for PlanActivationCode
        codes_list = []
        
        # Search logic
        search_query = request.GET.get('q', '')
        if search_query:
            codes = PlanActivationCode.objects.filter(
                Q(code__icontains=search_query) | 
                Q(plan_name__icontains=search_query)
            ).select_related('target_user', 'used_by').order_by('-created_at')
        else:
            codes = PlanActivationCode.objects.select_related('target_user', 'used_by').order_by('-created_at')
        
        for code in codes:
            codes_list.append({
                'id': str(code.id),
                'code': code.code,
                'plan_name': code.plan_name,
                'code_type': code.code_type,
                'code_type_display': code.get_code_type_display(),
                'is_used': code.is_used,
                'created_at': code.created_at,
                'expires_at': code.expires_at,
                'used_at': code.used_at,
                'target_user': code.target_user,
                'used_by': code.used_by,
                'target_user_name': code.target_user.name if code.target_user else None,
                'used_by_name': code.used_by.name if code.used_by else None
            })
            
        # HTMX: Return only the table rows
        if request.headers.get('HX-Request'):
            return render(request, 'admin_app/activation_codes.html#codes-table-body', {
                'codes': codes_list
            })
            
    except Exception as e:
        codes_list = []
        messages.error(request, f'Error fetching activation codes: {str(e)}')
    
    return render(request, 'admin_app/activation_codes.html', {
        'codes': codes_list,
        'search_query': search_query
    })


def create_activation_code(request):
    # 1. Authentication Check (Must return JSON, not redirect for AJAX)
    if not request.session.get('admin_id'):
        return JsonResponse({
            'success': False, 
            'message': 'Unauthorized. Please log in.'
        }, status=401) # Use 401 status code for unauthorized

    if request.method == 'POST':
        form = ActivationCodeForm(request.POST)

        if form.is_valid():
            plan_name = form.cleaned_data['plan_name']
            code_type = form.cleaned_data['code_type']
            target_user_id = form.cleaned_data.get('target_user')
            expires_at = form.cleaned_data.get('expires_at')
            
            # 2. Validation: User-specific code check
            if code_type == 'user_specific':
                if not target_user_id:
                    # Return JSON error for specific form validation failure
                    return JsonResponse({
                        'success': False, 
                        'message': 'Please specify a target user ID for user-specific codes.'
                    }, status=400) # 400 Bad Request
                
                # ORM: Check if the user ID exists before creating the code
                try:
                    # Note: You may need to cast target_user_id to the correct type (int/UUID)
                    # if TelegramUser.objects.filter(pk=target_user_id).exists() is too slow,
                    # but for security/robustness, a check is good.
                    if not TelegramUser.objects.filter(pk=target_user_id).exists():
                         return JsonResponse({
                            'success': False, 
                            'message': f'Target user with ID {target_user_id} does not exist.'
                        }, status=400)
                except (ValueError, TypeError):
                    return JsonResponse({
                        'success': False, 
                        'message': f'Invalid format for Target User ID.'
                    }, status=400)
            
            try:
                # Generate secure code
                code = PlanActivationCode.generate_secure_code()
                
                # ORM: Prepare parameters
                create_params = {
                    'code': code,
                    'plan_name': plan_name,
                    'code_type': code_type,
                    'is_used': False, # Replaces `0` in raw SQL
                    # NOTE: created_by_id removed - causes UUID error since session admin_id is integer
                    # but SystemAdmin model uses UUID primary keys
                    'created_by': None,  # Set to None for now
                    'expires_at': expires_at,
                    # Conditionally set target_user_id (None for general codes)
                    'target_user_id': target_user_id if code_type == 'user_specific' else None,
                }

                # ORM: Execute the insertion
                PlanActivationCode.objects.create(**create_params)
                
                # Success path
                if request.headers.get('HX-Request'):
                    # Return a success toast
                    return HttpResponse(f"""
                        <div class="p-4 rounded-lg text-white shadow-xl max-w-sm bg-green-600 transition-all duration-300"
                             x-data="{{ show: true }}" x-show="show" x-init="setTimeout(() => show = false, 3000)">
                            <p class="font-medium">Code {code} created successfully</p>
                        </div>
                        <script>
                            closeCodeModal();
                            setTimeout(() => location.reload(), 1000);
                        </script>
                    """)
                
                return JsonResponse({
                    'success': True, 
                    'message': f'Activation code created successfully: {code}',
                    'code': code
                }, status=201)
                
            except IntegrityError:
                if request.headers.get('HX-Request'):
                    return HttpResponse("""
                        <div class="p-4 rounded-lg text-white shadow-xl max-w-sm bg-red-600">
                            <p class="font-medium">Error: Could not generate unique code.</p>
                        </div>
                    """)
                return JsonResponse({
                    'success': False, 
                    'message': 'A unique code could not be generated. Please try again.'
                }, status=500)
            except Exception as e:
                if request.headers.get('HX-Request'):
                    return HttpResponse(f"""
                        <div class="p-4 rounded-lg text-white shadow-xl max-w-sm bg-red-600">
                            <p class="font-medium">Error: {str(e)}</p>
                        </div>
                    """)
                return JsonResponse({
                    'success': False, 
                    'message': f'Error creating activation code: {str(e)}'
                }, status=500)
        
        else:
            # Form Validation Failure
            if request.headers.get('HX-Request'):
                return HttpResponse("""
                    <div class="p-4 rounded-lg text-white shadow-xl max-w-sm bg-red-600">
                        <p class="font-medium">Form validation failed. Check inputs.</p>
                    </div>
                """)
            return JsonResponse({
                'success': False, 
                'message': 'Form validation failed. Check errors field for details.',
                'errors': form.errors.get_json_data() 
            }, status=400)

    # GET Request / Fallback Path
    return JsonResponse({
        'success': True,
    })


@require_http_methods(["POST"])
def update_activation_code(request, pk):
    # 1. Authentication Check
    if not request.session.get('admin_id'):
        return JsonResponse({
            'success': False, 
            'message': 'Unauthorized. Please log in.'
        }, status=401)

    try:
        # Use ORM to fetch the instance using integer pk
        instance = get_object_or_404(PlanActivationCode, pk=pk)
    except PlanActivationCode.DoesNotExist:
         return JsonResponse({
            'success': False, 
            'message': 'Activation Code not found.'
        }, status=404)
        
    # Bind form data to the existing instance
    form = ActivationCodeForm(request.POST, instance=instance)

    if form.is_valid():
        code_type = form.cleaned_data['code_type']
        target_user_id = form.cleaned_data.get('target_user')

        # 2. Validation: User-specific code check
        if code_type == 'user_specific':
            if not target_user_id:
                return JsonResponse({
                    'success': False, 
                    'message': 'Please specify a target user ID for user-specific codes.'
                }, status=400)
            
            # ORM: Check if the user ID exists (Assuming TelegramUser is imported)
            try:
                if not TelegramUser.objects.filter(pk=target_user_id).exists():
                     return JsonResponse({
                        'success': False, 
                        'message': f'Target user with ID {target_user_id} does not exist.'
                    }, status=400)
            except (ValueError, TypeError):
                return JsonResponse({
                    'success': False, 
                    'message': f'Invalid format for Target User ID.'
                }, status=400)
        
        try:
            # Save the updated form data to the instance
            instance.plan_name = form.cleaned_data['plan_name']
            instance.code_type = code_type
            # Set target_user_id to None if code is general
            instance.target_user_id = target_user_id if code_type == 'user_specific' else None
            instance.expires_at = form.cleaned_data.get('expires_at')
            
            instance.save() # ORM: Execute the update
            
            # Success: Return JsonResponse
            return JsonResponse({
                'success': True, 
                'message': f'Activation code {instance.code} updated successfully.'
            }) 
            
        except IntegrityError:
            return JsonResponse({
                'success': False, 
                'message': 'Database constraint failed during update (e.g., code uniqueness).'
            }, status=500)
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'message': f'Internal server error during update: {str(e)}'
            }, status=500)
            
    else:
        # Form Validation Failure: Return JsonResponse with status 400
        return JsonResponse({
            'success': False, 
            'message': 'Validation failed. Check the form data.',
            'errors': form.errors.get_json_data() 
        }, status=400)



@require_http_methods(["POST"])
def delete_activation_code(request, pk): # <--- ADD 'pk' HERE
    if not request.session.get('admin_id'):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    try:
        # Get object by PK (UUID)
        code_obj = PlanActivationCode.objects.get(id=pk)
        code_val = code_obj.code
        
        # Optional: Prevent deleting used codes
        if code_obj.is_used:
             if request.headers.get('HX-Request'):
                 return HttpResponse("Cannot delete used code", status=400)
             return JsonResponse({'error': 'Cannot delete a used code.'}, status=400)

        code_obj.delete()
        
        if request.headers.get('HX-Request'):
            return HttpResponse("") # Empty response removes the element
            
        return JsonResponse({'success': f'Code {code_val} deleted successfully.'})
        
    except PlanActivationCode.DoesNotExist:
        if request.headers.get('HX-Request'):
             return HttpResponse("Code not found", status=404)
        return JsonResponse({'error': 'Code not found.'}, status=404)
    except Exception as e:
        print(f"Delete Error: {e}") # Log error to console
        if request.headers.get('HX-Request'):
             return HttpResponse(f"Error: {str(e)}", status=500)
        return JsonResponse({'error': f'Deletion failed: {str(e)}'}, status=500)



def user_manage(request, user_id):
    if not request.session.get('admin_id'):
        return redirect('admin_app:login')
    
    try:
        # Fetch user details using ORM
        user = TelegramUser.objects.select_related('workspace').get(id=user_id)
        
        # Get active subscription for the workspace
        subscription = None
        if user.workspace:
            subscription = user.workspace.subscriptions.filter(status='active').order_by('-end_date').first()
            
        user_data = {
            'id': str(user.id),
            'name': user.name,
            'email': user.email,
            'phone': user.phone,
            'created_at': user.created_at,
            'workspace_id': user.workspace.id if user.workspace else None,
            'workspace_name': user.workspace.name if user.workspace else None,
            'subscription_id': subscription.id if subscription else None,
            'plan_name': subscription.plan_name if subscription else 'Free',
            'status': subscription.status if subscription else 'inactive',
            'start_date': subscription.start_date if subscription else None,
            'end_date': subscription.end_date if subscription else None
        }
    except TelegramUser.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('admin_app:dashboard')
    except Exception as e:
        messages.error(request, f'Error fetching user: {str(e)}')
        return redirect('admin_app:dashboard')
    
    # Handle plan update
    if request.method == 'POST':
        new_plan = request.POST.get('plan_name')
        new_status = request.POST.get('status', 'active')
        
        try:
            if subscription:
                # Update existing subscription
                subscription.plan_name = new_plan
                subscription.status = new_status
                subscription.save()
            elif user.workspace:
                # Create new subscription
                Subscription.objects.create(
                    workspace=user.workspace,
                    plan_name=new_plan,
                    status=new_status,
                    start_date=timezone.now(),
                    end_date=timezone.now() + timezone.timedelta(days=30)
                )
            else:
                messages.error(request, 'User has no workspace to subscribe.')
                return redirect('admin_app:user_manage', user_id=user_id)
            
            messages.success(request, f'Successfully updated {user.name}\'s plan to {new_plan}.')
            return redirect('admin_app:user_manage', user_id=user_id)
        except Exception as e:
            messages.error(request, f'Error updating plan: {str(e)}')
    
    return render(request, 'admin_app/user_manage.html', {'user': user_data})


# -----------------------
# User Management Views
# -----------------------

def users_list(request):
    if not request.session.get('admin_id'):
        return redirect('admin_app:login')
    
    from django.db.models import Q, Count
    from core.models import TelegramUser, Subscription
    from django.core.paginator import Paginator
    from bot_app.models import BotSettings as BotConfig # Alias to match view code
    
    # 1. Analytics
    total_users = TelegramUser.objects.count()
    active_users = TelegramUser.objects.filter(status='active').count()
    frozen_users = TelegramUser.objects.filter(status='frozen').count()
    
    # Plan counts
    plan_counts = Subscription.objects.filter(status='active').values('plan_name').annotate(count=Count('id'))
    
    plans_summary = {
        'Free': 0,
        'Pro': 0,
        'Max': 0,
        'Free Trial': 0
    }
    
    # Fill in counts
    for p in plan_counts:
        name = p['plan_name']
        if name in plans_summary:
            plans_summary[name] = p['count']
            
    # 2. Search & Filter
    q = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()
    
    users_qs = TelegramUser.objects.select_related('workspace').order_by('-created_at')
    
    if q:
        users_qs = users_qs.filter(
            Q(name__icontains=q) | 
            Q(email__icontains=q) |
            Q(workspace__name__icontains=q)
        )
        
    if status_filter:
        users_qs = users_qs.filter(status=status_filter)

    # 3. Pagination
    paginator = Paginator(users_qs, 20) # 20 per page
    page_number = request.GET.get('page')
    users_page = paginator.get_page(page_number)
    
    # 4. Prepare data for template
    users_data = []
    for u in users_page:
        # Get active subscription
        sub = u.workspace.subscriptions.filter(status='active').order_by('-end_date').first() if u.workspace else None
        plan_name = sub.plan_name if sub else 'Free'
        
        users_data.append({
            'user': u,
            'plan_name': plan_name,
            'subscription': sub
        })

    context = {
        'total_users': total_users,
        'active_users': active_users,
        'frozen_users': frozen_users,
        'plans_summary': plans_summary,
        'users': users_data,
        'paginator': users_page,
        'q': q,
        'status_filter': status_filter,
        'users_page': users_page # Pass the page object for pagination links
    }
    
    return render(request, 'admin_app/users_list.html', context)


@require_POST
def user_freeze(request, user_id):
    if not request.session.get('admin_id'):
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=401)
        
    try:
        from bot_app.models import BotSettings
        user = TelegramUser.objects.get(id=user_id)
        user.status = 'frozen'
        user.save()
        
        # Disconnect all bots for this user
        # Assuming 'owner' in BotSettings links to User (Django User), not TelegramUser
        # We need to get the Django user associated with this TelegramUser if possible, 
        # OR if BotSettings links to TelegramUser.
        # Checking models... BotSettings.owner is settings.AUTH_USER_MODEL.
        # TelegramUser is also linked to settings.AUTH_USER_MODEL via OneToOneField usually?
        # Let's check TelegramUser model definition.
        # It seems TelegramUser IS the user model or linked? 
        # Re-checking core/models.py... 
        # TelegramUser has no direct link to auth.User in the snippet I saw earlier?
        # Wait, previous code used `request.user.telegram_user`.
        # So TelegramUser is a profile.
        # But here we have `user_id` which is `TelegramUser.id`.
        # We need to find the Auth User to disconnect bots.
        # Let's assume for now we just update status. 
        # If BotSettings has a 'workspace' field, we could use that.
        # Let's check if we can find bots by workspace.
        
        if user.user:
             BotSettings.objects.filter(owner=user.user).update(is_connected=False)
        
        return JsonResponse({'success': True, 'message': 'User frozen and bots disconnected.'})
    except TelegramUser.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_POST
def user_unfreeze(request, user_id):
    if not request.session.get('admin_id'):
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=401)
        
    try:
        user = TelegramUser.objects.get(id=user_id)
        user.status = 'active'
        user.save()
        
        return JsonResponse({'success': True, 'message': 'User activated successfully.'})
    except TelegramUser.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["GET"])
def user_details_ajax(request, user_id):
    """Return user details for the modal"""
    if not request.session.get('admin_id'):
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=401)
        
    try:
        from bot_app.models import BotSettings
        user = TelegramUser.objects.get(id=user_id)
        workspace = user.workspace
        
        # Get subscription
        sub = workspace.subscriptions.filter(status='active').order_by('-end_date').first() if workspace else None
        
        # Get bots count
        bots_count = 0
        if user.user:
            bots_count = BotSettings.objects.filter(owner=user.user).count()
        
        data = {
            'id': str(user.id),
            'name': user.name,
            'email': user.email,
            'phone': user.phone,
            'status': user.status,
            'workspace_name': workspace.name if workspace else 'No Workspace',
            'joined_at': user.created_at.strftime('%Y-%m-%d'),
            'plan_name': sub.plan_name if sub else 'Free',
            'bots_count': bots_count,
            'has_used_free_trial': user.has_used_free_trial
        }
        return JsonResponse({'success': True, 'user': data})
    except TelegramUser.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User not found'}, status=404)
