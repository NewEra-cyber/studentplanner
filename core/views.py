from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.conf import settings
from core.models import (
    Schedule, UserProfile, JKUATTimetable, ActivityResource, 
    ResourceCategory, UserResourcePreference, Task, ProgressTracker,
    UserTimetable, SmartActivity, DailyFocus
)
from core.smart_scheduler import SmartScheduler
import pytz
from datetime import datetime, time, timedelta
import json
import os
import requests

def get_weather_data(location="Juja, KE"):
    """
    Get weather data from OpenWeatherMap API or return fallback data
    """
    api_key = getattr(settings, 'WEATHER_API_KEY', 'd10d7bf01e10146ffe0f12634e961152')
    
    try:
        # Try to get live weather data
        url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Map weather conditions to background classes and icons
            weather_mapping = {
                'clear': {'class': 'weather-sunny', 'icon': '☀️'},
                'clouds': {'class': 'weather-cloudy', 'icon': '☁️'},
                'rain': {'class': 'weather-rain', 'icon': '🌧️'},
                'drizzle': {'class': 'weather-rain', 'icon': '🌦️'},
                'thunderstorm': {'class': 'weather-storm', 'icon': '⛈️'},
                'snow': {'class': 'weather-snow', 'icon': '❄️'},
                'mist': {'class': 'weather-fog', 'icon': '🌫️'},
                'fog': {'class': 'weather-fog', 'icon': '🌫️'},
                'haze': {'class': 'weather-fog', 'icon': '🌫️'},
            }
            
            weather_main = data['weather'][0]['main'].lower()
            weather_info = weather_mapping.get(weather_main, {'class': 'weather-default', 'icon': '🌤️'})
            
            return {
                'location_name': data['name'],
                'temperature': round(data['main']['temp']),
                'feels_like': round(data['main']['feels_like']),
                'humidity': data['main']['humidity'],
                'wind_speed': round(data['wind']['speed'] * 3.6),  # Convert m/s to km/h
                'pressure': data['main']['pressure'],
                'description': data['weather'][0]['description'].title(),
                'icon': weather_info['icon'],
                'background_class': weather_info['class'],
                'source': 'openweathermap'
            }
    
    except Exception as e:
        print(f"Weather API error: {e}")
    
    # Fallback data if API fails
    return {
        'location_name': 'Juja',
        'temperature': 24,
        'feels_like': 26,
        'humidity': 65,
        'wind_speed': 12,
        'pressure': 1013,
        'description': 'Partly Cloudy',
        'icon': '🌤️',
        'background_class': 'weather-cloudy',
        'source': 'fallback'
    }

@login_required
def dashboard(request):
    """Main dashboard view with integrated smart scheduling"""
    selected_day = request.GET.get('day', None)
    
    nairobi_tz = pytz.timezone('Africa/Nairobi')
    now_nairobi = timezone.now().astimezone(nairobi_tz)
    
    if selected_day:
        try:
            selected_date = datetime.strptime(selected_day, '%Y-%m-%d').date()
            current_day = selected_date.strftime('%A')
        except:
            selected_date = now_nairobi.date()
            current_day = now_nairobi.strftime('%A')
    else:
        selected_date = now_nairobi.date()
        current_day = now_nairobi.strftime('%A')
    
    # Calculate previous and next days
    prev_day = selected_date - timedelta(days=1)
    next_day = selected_date + timedelta(days=1)
    
    # Get SMART activities (gentleman routine)
    smart_activities = SmartActivity.objects.filter(
        user=request.user,
        day=current_day,
        is_active=True
    ).order_by('start_time')
    
    # Get timetable entries (academic schedule)
    jkuat_schedule = JKUATTimetable.objects.filter(
        user=request.user, 
        day=current_day
    ).order_by('start_time')
    
    user_timetable = UserTimetable.objects.filter(
        user=request.user,
        day=current_day
    ).order_by('start_time')
    
    # Get personal activities
    personal_schedule = Schedule.objects.filter(
        user=request.user, 
        day=current_day
    ).order_by('start_time')
    
    # Combine ALL schedules (Smart + Timetable + Personal)
    today_schedule = list(smart_activities) + list(jkuat_schedule) + list(user_timetable) + list(personal_schedule)
    today_schedule.sort(key=lambda x: x.start_time)
    
    # Get or create user profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Get today's progress
    today_progress = ProgressTracker.objects.filter(
        user=request.user,
        date=selected_date
    ).first()
    
    # Get quick stats
    today_tasks = Task.objects.filter(
        user=request.user,
        due_date=selected_date,
        status__in=['todo', 'in_progress']
    ).count()
    
    # Get daily focus quote
    daily_focus = DailyFocus.objects.filter(is_active=True).order_by('?').first()
    
    # Calculate consistency score
    completed_activities = SmartActivity.objects.filter(
        user=request.user,
        last_adjusted__date=selected_date
    ).count()
    total_smart_activities = smart_activities.count()
    consistency_score = (completed_activities / total_smart_activities * 100) if total_smart_activities > 0 else 0
    
    # Get last adjustment time
    last_adjusted_activity = SmartActivity.objects.filter(
        user=request.user,
        last_adjusted__isnull=False
    ).order_by('-last_adjusted').first()
    
    # Find current and next activity
    current_activity = None
    next_activity = None
    current_time = now_nairobi.time()
    
    for activity in today_schedule:
        if activity.start_time <= current_time <= activity.end_time:
            current_activity = activity
        elif activity.start_time > current_time and next_activity is None:
            next_activity = activity
    
    # Calculate next 7 days
    next_7_days = []
    for i in range(7):
        day_date = selected_date + timedelta(days=i)
        day_name = day_date.strftime('%a')
        next_7_days.append({
            'date': day_date,
            'day_name': day_name,
            'is_selected': day_date == selected_date
        })
    
    # GET WEATHER DATA - This is the missing piece!
    weather = get_weather_data()
    
    context = {
        'current_time': now_nairobi,
        'current_day': current_day,
        'selected_date': selected_date,
        'prev_day': prev_day,
        'next_day': next_day,
        'today_schedule': today_schedule,
        'smart_activities': smart_activities,
        'jkuat_schedule': jkuat_schedule,
        'user_timetable': user_timetable,
        'personal_schedule': personal_schedule,
        'no_classes_today': len(jkuat_schedule) == 0 and len(user_timetable) == 0,
        'profile': profile,
        'today': now_nairobi.date(),
        'is_today': selected_date == now_nairobi.date(),
        'today_progress': today_progress,
        'today_tasks': today_tasks,
        'current_activity': current_activity,
        'next_activity': next_activity,
        'next_7_days': next_7_days,
        'daily_focus': daily_focus,
        'consistency_score': round(consistency_score, 1),
        'last_adjusted_activity': last_adjusted_activity,
        'weather': weather,  # ADD WEATHER DATA TO CONTEXT
    }
    
    return render(request, 'dashboard.html', context)

@login_required
def timetable_input(request):
    """Manual timetable input page with auto-adjustment and conditional fields"""
    if request.method == 'POST':
        day = request.POST.get('day')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        activity_type = request.POST.get('activity_type', 'lecture')
        
        # Define academic activity types
        ACADEMIC_TYPES = ['lecture', 'lab', 'review']
        
        # Check if this is an academic activity
        is_academic = activity_type in ACADEMIC_TYPES
        
        if is_academic:
            # For academic activities, require unit code and unit name
            unit_code = request.POST.get('unit_code', '').strip()
            unit_name = request.POST.get('unit_name', '').strip()
            venue = request.POST.get('venue', '').strip()
            
            if not unit_code or not unit_name:
                # Add error message or return error
                return redirect('timetable_input')
            
            # Create academic timetable entry
            UserTimetable.objects.create(
                user=request.user,
                day=day,
                start_time=start_time,
                end_time=end_time,
                unit_code=unit_code,
                unit_name=unit_name,
                venue=venue,
                activity_type=activity_type
            )
        else:
            # For personal activities, use activity name
            activity_name = request.POST.get('activity_name', '').strip()
            location = request.POST.get('location', '').strip()
            
            if not activity_name:
                # Add error message or return error
                return redirect('timetable_input')
            
            # Create personal activity entry
            UserTimetable.objects.create(
                user=request.user,
                day=day,
                start_time=start_time,
                end_time=end_time,
                unit_code='PERSONAL',  # Generic code for personal activities
                unit_name=activity_name,
                venue=location,
                activity_type=activity_type
            )
        
        # AUTO-ADJUST: Trigger smart scheduler immediately
        scheduler = SmartScheduler(request.user)
        scheduler.adjust_schedule_for_timetable(day)
        
        return redirect('timetable_input')
    
    # Get existing timetable entries grouped by day
    timetable_entries = UserTimetable.objects.filter(user=request.user).order_by('day', 'start_time')
    timetable_by_day = {}
    
    for entry in timetable_entries:
        if entry.day not in timetable_by_day:
            timetable_by_day[entry.day] = []
        timetable_by_day[entry.day].append(entry)
    
    context = {
        'timetable_by_day': timetable_by_day,
        'days': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
        'activity_types': Schedule.ACTIVITY_TYPES,
    }
    return render(request, 'timetable_input.html', context)
@login_required
def delete_timetable_entry(request, entry_id):
    """Delete a timetable entry and auto-adjust schedule"""
    entry = get_object_or_404(UserTimetable, id=entry_id, user=request.user)
    day = entry.day
    entry.delete()
    
    # AUTO-ADJUST: Trigger smart scheduler after deletion
    scheduler = SmartScheduler(request.user)
    scheduler.adjust_schedule_for_timetable(day)
    
    return redirect('timetable_input')

@login_required
def adjust_schedule_manual(request):
    """Manually trigger schedule adjustment for a specific day"""
    if request.method == 'POST':
        day = request.POST.get('day')
        
        scheduler = SmartScheduler(request.user)
        scheduler.adjust_schedule_for_timetable(day)
        
        return JsonResponse({
            'success': True,
            'message': f'✅ Schedule automatically adjusted for {day}!'
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
def generate_schedule_from_timetable(request):
    """Generate personal schedule from timetable (DEPRECATED - now auto)"""
    if request.method == 'POST':
        return JsonResponse({
            'success': True,
            'message': '✅ Schedule auto-adjusts when you add timetable entries!'
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
def clear_timetable(request):
    """Clear all timetable entries and reset schedule"""
    if request.method == 'POST':
        # Get all days before deleting
        days = UserTimetable.objects.filter(user=request.user).values_list('day', flat=True).distinct()
        
        # Delete timetable
        UserTimetable.objects.filter(user=request.user).delete()
        
        # Reset schedule for each affected day
        scheduler = SmartScheduler(request.user)
        for day in days:
            scheduler.adjust_schedule_for_timetable(day)
        
        return JsonResponse({'success': True, 'message': 'Timetable cleared and schedule reset!'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
def profile_page(request):
    """User profile page"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()
        
        profile.first_name = request.POST.get('first_name', profile.first_name)
        profile.last_name = request.POST.get('last_name', profile.last_name)
        profile.course = request.POST.get('course', profile.course)
        profile.weight = request.POST.get('weight') or profile.weight
        profile.height = request.POST.get('height') or profile.height
        profile.wake_up_time = request.POST.get('wake_up_time') or profile.wake_up_time
        profile.sleep_time = request.POST.get('sleep_time') or profile.sleep_time
        profile.current_phase = request.POST.get('current_phase') or profile.current_phase
        profile.streak_count = request.POST.get('streak_count') or profile.streak_count
        profile.total_points = request.POST.get('total_points') or profile.total_points
        
        # Handle theme
        theme = request.POST.get('theme')
        if theme in ['light', 'dark', 'auto']:
            profile.theme = theme
        
        # Handle profile photo upload
        if 'profile_photo' in request.FILES:
            profile.profile_photo = request.FILES['profile_photo']
        
        profile.save()
        return redirect('profile')
    
    # Get user statistics
    total_tasks = Task.objects.filter(user=request.user).count()
    completed_tasks = Task.objects.filter(user=request.user, status='completed').count()
    current_streak = profile.streak_count
    
    context = {
        'profile': profile,
        'user': request.user,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'current_streak': current_streak,
    }
    return render(request, 'profile.html', context)

@login_required
def manage_activities(request):
    """Activity management"""
    personal_activities = Schedule.objects.filter(user=request.user).order_by('day', 'start_time')
    jkuat_activities = JKUATTimetable.objects.filter(user=request.user).order_by('day', 'start_time')
    user_timetable_activities = UserTimetable.objects.filter(user=request.user).order_by('day', 'start_time')
    smart_activities = SmartActivity.objects.filter(user=request.user).order_by('day', 'start_time')
    
    if request.method == 'POST':
        if 'delete_activity' in request.POST:
            activity_id = request.POST.get('delete_activity')
            try:
                activity = Schedule.objects.get(id=activity_id, user=request.user)
                activity.delete()
            except Schedule.DoesNotExist:
                pass
        return redirect('manage_activities')
    
    # Group activities by day
    activities_by_day = {}
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    for day in days_order:
        activities_by_day[day] = []
    
    for activity in personal_activities:
        if activity.day not in activities_by_day:
            activities_by_day[activity.day] = []
        activities_by_day[activity.day].append(activity)
    
    for activity in jkuat_activities:
        if activity.day not in activities_by_day:
            activities_by_day[activity.day] = []
        activities_by_day[activity.day].append(activity)
    
    for activity in user_timetable_activities:
        if activity.day not in activities_by_day:
            activities_by_day[activity.day] = []
        activities_by_day[activity.day].append(activity)
    
    for activity in smart_activities:
        if activity.day not in activities_by_day:
            activities_by_day[activity.day] = []
        activities_by_day[activity.day].append(activity)
    
    context = {
        'activities_by_day': activities_by_day,
        'days_order': days_order,
    }
    return render(request, 'manage_activities.html', context)

@login_required
def activities_resources(request):
    """Resources view with comprehensive resource database"""
    activity_type = request.GET.get('type', '')
    
    nairobi_tz = pytz.timezone('Africa/Nairobi')
    now_nairobi = timezone.now().astimezone(nairobi_tz)
    current_day = now_nairobi.strftime('%A')
    
    jkuat_schedule = JKUATTimetable.objects.filter(
        user=request.user, 
        day=current_day
    ).order_by('start_time')
    
    user_timetable = UserTimetable.objects.filter(
        user=request.user,
        day=current_day
    ).order_by('start_time')
    
    personal_schedule = Schedule.objects.filter(
        user=request.user, 
        day=current_day
    ).order_by('start_time')
    
    today_schedule = list(jkuat_schedule) + list(user_timetable) + list(personal_schedule)
    today_schedule.sort(key=lambda x: x.start_time)
    
    categories = ResourceCategory.objects.filter(is_active=True).prefetch_related('resources')
    
    user_favorites = UserResourcePreference.objects.filter(
        user=request.user,
        is_favorite=True
    ).select_related('resource', 'resource__category')
    
    # Calculate total resources count
    total_resources = ActivityResource.objects.filter(is_active=True).count()
    free_resources = ActivityResource.objects.filter(is_active=True, is_free=True).count()
    
    context = {
        'activity_type': activity_type,
        'today_schedule': today_schedule,
        'current_day': current_day,
        'categories': categories,
        'user_favorites': user_favorites,
        'total_resources': total_resources,
        'free_resources': free_resources,
    }
    return render(request, 'activities_resources.html', context)

@login_required
def resource_detail(request, resource_id):
    """Display detailed view of a specific resource"""
    resource = get_object_or_404(ActivityResource, id=resource_id, is_active=True)
    
    is_favorite = UserResourcePreference.objects.filter(
        user=request.user,
        resource=resource,
        is_favorite=True
    ).exists()
    
    context = {
        'resource': resource,
        'is_favorite': is_favorite,
    }
    
    return render(request, 'resource/resource_detail.html', context)

@login_required
def resource_by_category(request, category_id):
    """Display resources filtered by category"""
    category = get_object_or_404(ResourceCategory, id=category_id, is_active=True)
    resources = ActivityResource.objects.filter(
        category=category,
        is_active=True
    ).order_by('name')
    
    user_favorites = UserResourcePreference.objects.filter(
        user=request.user,
        is_favorite=True
    ).values_list('resource_id', flat=True)
    
    context = {
        'category': category,
        'resources': resources,
        'user_favorites': user_favorites,
    }
    
    return render(request, 'resource/category_resources.html', context)

@login_required
def resource_by_activity_type(request, activity_type):
    """Display resources filtered by activity type"""
    resources = ActivityResource.objects.filter(
        activity_type=activity_type,
        is_active=True
    ).order_by('category', 'name')
    
    user_favorites = UserResourcePreference.objects.filter(
        user=request.user,
        is_favorite=True
    ).values_list('resource_id', flat=True)
    
    context = {
        'activity_type': activity_type,
        'resources': resources,
        'user_favorites': user_favorites,
    }
    
    return render(request, 'resource/category_resources.html', context)

@login_required
def my_favorites(request):
    """Display user's favorite resources"""
    user_favorites = UserResourcePreference.objects.filter(
        user=request.user,
        is_favorite=True
    ).select_related('resource', 'resource__category')
    
    context = {
        'user_favorites': user_favorites,
    }
    
    return render(request, 'resource/category_resources.html', context)

@login_required
def search_resources(request):
    """Search resources"""
    query = request.GET.get('q', '')
    resources = []
    
    if query:
        resources = ActivityResource.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query),
            is_active=True
        ).order_by('category', 'name')
    
    user_favorites = UserResourcePreference.objects.filter(
        user=request.user,
        is_favorite=True
    ).values_list('resource_id', flat=True)
    
    context = {
        'resources': resources,
        'query': query,
        'user_favorites': user_favorites,
    }
    
    return render(request, 'resource/category_resources.html', context)

@csrf_exempt
@login_required
def toggle_favorite(request, resource_id):
    """Toggle favorite status for a resource"""
    if request.method == 'POST':
        try:
            resource = get_object_or_404(ActivityResource, id=resource_id, is_active=True)
            
            preference, created = UserResourcePreference.objects.get_or_create(
                user=request.user,
                resource=resource
            )
            
            preference.is_favorite = not preference.is_favorite
            preference.save()
            
            return JsonResponse({
                'success': True,
                'is_favorite': preference.is_favorite,
                'message': 'Favorite status updated'
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def class_notes(request):
    """Display class notes page with folders and files"""
    notes_dir = os.path.join(settings.MEDIA_ROOT, 'class_notes')
    
    if not os.path.exists(notes_dir):
        os.makedirs(notes_dir)
    
    folders = []
    files = []
    
    if os.path.exists(notes_dir):
        for item in os.listdir(notes_dir):
            item_path = os.path.join(notes_dir, item)
            if os.path.isdir(item_path):
                file_count = len([f for f in os.listdir(item_path) if os.path.isfile(os.path.join(item_path, f))])
                folders.append({
                    'name': item,
                    'file_count': file_count,
                    'path': item_path
                })
            else:
                files.append({
                    'name': item,
                    'size': os.path.getsize(item_path),
                    'path': item_path
                })
    
    context = {
        'folders': folders,
        'files': files,
    }
    return render(request, 'class_notes.html', context)

@csrf_exempt
@login_required
def create_folder(request):
    """Create a new folder for class notes"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            folder_name = data.get('folder_name', '').strip()
            parent_folder = data.get('parent_folder', '').strip()
            
            if not folder_name:
                return JsonResponse({'success': False, 'error': 'Folder name is required'})
            
            folder_name = "".join(c for c in folder_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            
            if parent_folder:
                folder_path = os.path.join(settings.MEDIA_ROOT, 'class_notes', parent_folder, folder_name)
            else:
                folder_path = os.path.join(settings.MEDIA_ROOT, 'class_notes', folder_name)
            
            notes_dir = os.path.join(settings.MEDIA_ROOT, 'class_notes')
            if not os.path.exists(notes_dir):
                os.makedirs(notes_dir)
            
            if os.path.exists(folder_path):
                return JsonResponse({'success': False, 'error': 'Folder already exists'})
            
            os.makedirs(folder_path)
            return JsonResponse({'success': True, 'message': f'Folder "{folder_name}" created successfully'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
@login_required
def upload_file(request):
    """Upload a file to class notes"""
    if request.method == 'POST':
        try:
            folder = request.POST.get('folder', '').strip()
            
            if 'file' not in request.FILES:
                return JsonResponse({'success': False, 'error': 'No file provided'})
            
            uploaded_file = request.FILES['file']
            
            if folder:
                file_path = os.path.join(settings.MEDIA_ROOT, 'class_notes', folder, uploaded_file.name)
                folder_path = os.path.join(settings.MEDIA_ROOT, 'class_notes', folder)
            else:
                file_path = os.path.join(settings.MEDIA_ROOT, 'class_notes', uploaded_file.name)
                folder_path = os.path.join(settings.MEDIA_ROOT, 'class_notes')
            
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            
            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            
            return JsonResponse({'success': True, 'message': f'File "{uploaded_file.name}" uploaded successfully'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
@login_required
def create_file(request):
    """Create a new file in class notes"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            folder = data.get('folder', '').strip()
            filename = data.get('filename', '').strip()
            content = data.get('content', '')
            
            if not filename:
                return JsonResponse({'success': False, 'error': 'Filename is required'})
            
            if folder:
                file_path = os.path.join(settings.MEDIA_ROOT, 'class_notes', folder, filename)
                folder_path = os.path.join(settings.MEDIA_ROOT, 'class_notes', folder)
            else:
                file_path = os.path.join(settings.MEDIA_ROOT, 'class_notes', filename)
                folder_path = os.path.join(settings.MEDIA_ROOT, 'class_notes')
            
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            
            if os.path.exists(file_path):
                return JsonResponse({'success': False, 'error': 'File already exists'})
            
            with open(file_path, 'w') as f:
                f.write(content)
            
            return JsonResponse({'success': True, 'message': f'File "{filename}" created successfully'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
@login_required
def get_folder_content(request):
    """Get contents of a folder"""
    if request.method == 'GET':
        try:
            folder = request.GET.get('folder', '').strip()
            
            if folder:
                folder_path = os.path.join(settings.MEDIA_ROOT, 'class_notes', folder)
            else:
                folder_path = os.path.join(settings.MEDIA_ROOT, 'class_notes')
            
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            
            folders = []
            files = []
            
            for item in os.listdir(folder_path):
                item_path = os.path.join(folder_path, item)
                if os.path.isdir(item_path):
                    file_count = len([f for f in os.listdir(item_path) if os.path.isfile(os.path.join(item_path, f))])
                    folders.append({'name': item, 'file_count': file_count})
                else:
                    size = os.path.getsize(item_path)
                    size_str = f"{size / 1024:.2f} KB" if size < 1024*1024 else f"{size / (1024*1024):.2f} MB"
                    files.append({'name': item, 'size': size_str})
            
            return JsonResponse({'success': True, 'folders': folders, 'files': files})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
@login_required
def get_file_content(request):
    """Get contents of a file"""
    if request.method == 'GET':
        try:
            filename = request.GET.get('filename', '').strip()
            folder = request.GET.get('folder', '').strip()
            
            if not filename:
                return JsonResponse({'success': False, 'error': 'Filename is required'})
            
            if folder:
                file_path = os.path.join(settings.MEDIA_ROOT, 'class_notes', folder, filename)
            else:
                file_path = os.path.join(settings.MEDIA_ROOT, 'class_notes', filename)
            
            if not os.path.exists(file_path):
                return JsonResponse({'success': False, 'error': 'File not found'})
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            return JsonResponse({'success': True, 'content': content})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
@login_required
def generate_summary(request):
    """Generate AI summary of a file"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            filename = data.get('filename', '').strip()
            folder = data.get('folder', '').strip()
            
            if not filename:
                return JsonResponse({'success': False, 'error': 'Filename is required'})
            
            if folder:
                file_path = os.path.join(settings.MEDIA_ROOT, 'class_notes', folder, filename)
            else:
                file_path = os.path.join(settings.MEDIA_ROOT, 'class_notes', filename)
            
            if not os.path.exists(file_path):
                return JsonResponse({'success': False, 'error': 'File not found'})
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            lines = content.split('\n')
            summary = ' '.join(lines[:10]) if len(lines) > 10 else content[:500]
            
            key_points = [
                'Key point 1: Main concept',
                'Key point 2: Important detail',
                'Key point 3: Notable information',
            ]
            
            return JsonResponse({
                'success': True,
                'summary': summary,
                'key_points': key_points
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
@login_required
def launch_vscode(request):
    """Placeholder for VS Code launch"""
    if request.method == 'POST':
        try:
            return JsonResponse({
                'success': True,
                'message': 'VS Code launch initiated'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def toggle_dark_mode(request):
    """Simple dark mode toggle endpoint"""
    if request.method == 'POST':
        try:
            if 'dark_mode' in request.session:
                request.session['dark_mode'] = not request.session['dark_mode']
            else:
                request.session['dark_mode'] = True
            
            request.session.save()
            
            if request.user.is_authenticated:
                profile, created = UserProfile.objects.get_or_create(user=request.user)
                profile.theme = 'dark' if request.session['dark_mode'] else 'light'
                profile.save()
            
            return JsonResponse({
                'status': 'success',
                'dark_mode': request.session['dark_mode'],
                'message': 'Theme preference saved'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)