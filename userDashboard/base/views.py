from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.core.paginator import Paginator
from .models import User, Complaints, UserLoginSession, EmployeeCheckIn
from .forms import UserRegistrationForm, ComplaintForm, UserEditForm
from .middleware import get_client_ip, get_location_from_ip
from .websocket_utils import send_dashboard_update, send_complaint_update, send_new_complaint_notification, send_user_notification, send_admin_notification
import json

def is_admin(user):
    return user.is_authenticated and user.is_superuser

def is_employee(user):
    return user.is_authenticated and user.is_employee

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'base/login.html')

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')

@login_required
def dashboard(request):
    if request.user.is_superuser:
        # Admin dashboard
        total_employees = User.objects.filter(is_employee=True).count()
        total_complaints = Complaints.objects.count()
        pending_complaints = Complaints.objects.filter(status='Pending').count()
        in_progress_complaints = Complaints.objects.filter(status='In Progress').count()
        closed_complaints = Complaints.objects.filter(status='Closed').count()
        escalated_complaints = Complaints.objects.filter(status='Escalated').count()
        
        recent_complaints = Complaints.objects.select_related('assignee').order_by('-modified_date')[:10]
        
        context = {
            'total_employees': total_employees,
            'total_complaints': total_complaints,
            'pending_complaints': pending_complaints,
            'in_progress_complaints': in_progress_complaints,
            'closed_complaints': closed_complaints,
            'escalated_complaints': escalated_complaints,
            'recent_complaints': recent_complaints,
        }
        return render(request, 'base/admin_dashboard.html', context)
    
    elif request.user.is_employee:
        # Employee dashboard
        assigned_complaints = Complaints.objects.filter(assignee=request.user).order_by('-created_date')
        
        # Calculate statistics for assigned complaints
        total_assigned = assigned_complaints.count()
        pending_assigned = assigned_complaints.filter(status='Pending').count()
        in_progress_assigned = assigned_complaints.filter(status='In Progress').count()
        closed_assigned = assigned_complaints.filter(status='Closed').count()
        escalated_assigned = assigned_complaints.filter(status='Escalated').count()
        
        # Get current login session information
        current_session = UserLoginSession.objects.filter(
            user=request.user,
            is_active=True
        ).order_by('-login_datetime').first()
        
        # Get current check-in status
        current_checkin = EmployeeCheckIn.objects.filter(
            user=request.user,
            is_active=True,
            checkout_datetime__isnull=True
        ).first()
        
        # Get check-in history
        checkin_history = EmployeeCheckIn.objects.filter(
            user=request.user
        ).order_by('-checkin_datetime')
        
        # Paginate check-in history
        paginator = Paginator(checkin_history, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'assigned_complaints': assigned_complaints,
            'total_assigned': total_assigned,
            'pending_assigned': pending_assigned,
            'in_progress_assigned': in_progress_assigned,
            'closed_assigned': closed_assigned,
            'escalated_assigned': escalated_assigned,
            'current_session': current_session,
            'current_checkin': current_checkin,
            'checkin_history': page_obj,
        }
        return render(request, 'base/employee_dashboard.html', context)
    
    else:
        messages.error(request, 'Access denied. You need proper permissions.')
        return redirect('login')

@user_passes_test(is_admin)
def user_registration(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            messages.success(request, f'User {user.username} has been created successfully!')
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'base/user_registration.html', {'form': form})

@user_passes_test(is_admin)
def complaint_create(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.created_by = request.user
            complaint.save()
            
            # Send WebSocket notifications
            send_dashboard_update()
            send_new_complaint_notification({
                'id': complaint.id,
                'title': complaint.title,
                'status': complaint.status,
                'created_by': complaint.created_by.full_name
            })
            
            if request.user.is_superuser:
                send_admin_notification(f"New complaint created: {complaint.title}", "success")
            else:
                send_user_notification(request.user.id, f"Complaint '{complaint.title}' created successfully", "success")
            
            messages.success(request, 'Complaint created successfully!')
            return redirect('dashboard')
    else:
        form = ComplaintForm()
    
    return render(request, 'base/complaint_create.html', {'form': form})

@user_passes_test(is_employee)
def complaint_detail(request, complaint_id):
    complaint = get_object_or_404(Complaints, id=complaint_id, assignee=request.user)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        comments = request.POST.get('comments', '')
        
        if new_status in dict(Complaints._meta.get_field('status').choices):
            complaint.status = new_status
            complaint.comments = comments
            complaint.updated_by = request.user
            complaint.save()
            messages.success(request, 'Complaint status updated successfully!')
            return redirect('dashboard')
    
    return render(request, 'base/complaint_detail.html', {'complaint': complaint})

@csrf_exempt
@require_POST
@user_passes_test(is_employee)
def update_complaint_status(request):
    try:
        data = json.loads(request.body)
        complaint_id = data.get('complaint_id')
        new_status = data.get('status')
        comments = data.get('comments', '')
        
        complaint = get_object_or_404(Complaints, id=complaint_id, assignee=request.user)
        
        if new_status in dict(Complaints._meta.get_field('status').choices):
            # Require comments when escalating
            if new_status == 'Escalated' and not comments.strip():
                return JsonResponse({
                    'success': False,
                    'message': 'Comments are mandatory when escalating a complaint. Please provide a reason for escalation.'
                }, status=400)
            
            complaint.status = new_status
            complaint.comments = comments
            complaint.updated_by = request.user
            complaint.save()
            
            # Send WebSocket notifications
            send_dashboard_update()
            send_complaint_update(complaint.id, "status_updated")
            
            if request.user.is_superuser:
                send_admin_notification(f"Complaint '{complaint.title}' status updated to {new_status}", "info")
            else:
                send_user_notification(request.user.id, f"Complaint '{complaint.title}' status updated to {new_status}", "success")
            
            return JsonResponse({
                'success': True,
                'message': 'Status updated successfully'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Invalid status'
            }, status=400)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)

@user_passes_test(is_admin)
def complaint_edit(request, complaint_id):
    complaint = get_object_or_404(Complaints, id=complaint_id)
    
    if request.method == 'POST':
        form = ComplaintForm(request.POST, instance=complaint)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.updated_by = request.user
            complaint.save()
            messages.success(request, 'Complaint updated successfully!')
            return redirect('dashboard')
    else:
        form = ComplaintForm(instance=complaint)
    
    return render(request, 'base/complaint_edit.html', {'form': form, 'complaint': complaint})

@user_passes_test(is_admin)
def user_list(request):
    users = User.objects.filter(is_superuser=False).order_by('-date_joined')
    return render(request, 'base/user_list.html', {'users': users})

@user_passes_test(is_admin)
def user_edit(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User {user.username} updated successfully!')
            return redirect('user_list')
    else:
        form = UserEditForm(instance=user)
    
    return render(request, 'base/user_edit.html', {'form': form, 'user': user})

@user_passes_test(is_admin)
def debug_location(request):
    """Debug view to test IP geolocation"""
    ip_address = get_client_ip(request)
    location_info = get_location_from_ip(ip_address)
    
    # Get WiFi information
    wifi_info = None
    wifi_networks = []
    try:
        from .wifi_location import WiFiLocationService
        wifi_service = WiFiLocationService()
        wifi_networks = wifi_service.get_wifi_networks()
        if wifi_networks:
            wifi_info = wifi_service.get_location_from_wifi(wifi_networks)
    except Exception as e:
        print(f"Error getting WiFi info: {e}")
    
    context = {
        'ip_address': ip_address,
        'location_info': location_info,
        'wifi_info': wifi_info,
        'wifi_networks': wifi_networks[:10],  # Show first 10 networks
        'request_meta': {k: v for k, v in request.META.items() if 'IP' in k or 'REMOTE' in k}
    }
    
    return render(request, 'base/debug_location.html', context)

@user_passes_test(is_employee)
def check_in(request):
    """Employee check-in with location tracking"""
    if request.method == 'POST':
        # Check if already checked in
        active_checkin = EmployeeCheckIn.objects.filter(
            user=request.user,
            is_active=True,
            checkout_datetime__isnull=True
        ).first()
        
        if active_checkin:
            return JsonResponse({
                'success': False,
                'message': 'You are already checked in!'
            }, status=400)
        
        # Get location information
        ip_address = get_client_ip(request)
        location_info = get_location_from_ip(ip_address)
        
        # Create check-in record
        checkin = EmployeeCheckIn.objects.create(
            user=request.user,
            checkin_location=location_info.get('location', ''),
            ip_address=ip_address,
            created_by=request.user
        )
        
        # Send WebSocket notification
        send_user_notification(request.user.id, f"Checked in at {location_info.get('location', 'Unknown location')}", "success")
        send_admin_notification(f"Employee {request.user.full_name} checked in", "info")
        
        return JsonResponse({
            'success': True,
            'message': 'Successfully checked in!',
            'checkin_time': checkin.checkin_datetime.strftime('%Y-%m-%d %I:%M %p'),
            'location': location_info.get('location', 'Unknown location')
        })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

@user_passes_test(is_employee)
def check_out(request):
    """Employee check-out with location tracking"""
    if request.method == 'POST':
        # Find active check-in
        active_checkin = EmployeeCheckIn.objects.filter(
            user=request.user,
            is_active=True,
            checkout_datetime__isnull=True
        ).first()
        
        if not active_checkin:
            return JsonResponse({
                'success': False,
                'message': 'You are not currently checked in!'
            }, status=400)
        
        # Get location information
        ip_address = get_client_ip(request)
        location_info = get_location_from_ip(ip_address)
        
        # Update check-in record
        active_checkin.checkout_datetime = timezone.now()
        active_checkin.checkout_location = location_info.get('location', '')
        active_checkin.is_active = False
        active_checkin.updated_by = request.user
        active_checkin.save()
        
        # Calculate duration
        duration = active_checkin.duration
        duration_str = f"{duration.seconds // 3600}h {(duration.seconds % 3600) // 60}m" if duration else "Unknown"
        
        # Send WebSocket notification
        send_user_notification(request.user.id, f"Checked out. Duration: {duration_str}", "info")
        send_admin_notification(f"Employee {request.user.full_name} checked out after {duration_str}", "info")
        
        return JsonResponse({
            'success': True,
            'message': 'Successfully checked out!',
            'checkout_time': active_checkin.checkout_datetime.strftime('%Y-%m-%d %I:%M %p'),
            'duration': duration_str,
            'location': location_info.get('location', 'Unknown location')
        })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

@user_passes_test(is_employee)
def get_checkin_status(request):
    """Get current check-in status for employee"""
    active_checkin = EmployeeCheckIn.objects.filter(
        user=request.user,
        is_active=True,
        checkout_datetime__isnull=True
    ).first()
    
    if active_checkin:
        return JsonResponse({
            'checked_in': True,
            'checkin_time': active_checkin.checkin_datetime.strftime('%Y-%m-%d %I:%M %p'),
            'location': active_checkin.checkin_location or 'Unknown location'
        })
    else:
        return JsonResponse({
            'checked_in': False
        })

@user_passes_test(is_employee)
def checkin_history(request):
    """Show check-in/check-out history for employee"""
    checkin_history = EmployeeCheckIn.objects.filter(
        user=request.user
    ).order_by('-checkin_datetime')
    
    context = {
        'checkin_history': checkin_history
    }
    return render(request, 'base/checkin_history.html', context)
