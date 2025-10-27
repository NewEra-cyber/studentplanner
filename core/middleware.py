from django.utils import timezone
from .models import UserProfile
import pytz

class StreakMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Update user streak if authenticated
        if request.user.is_authenticated:
            try:
                profile, created = UserProfile.objects.get_or_create(user=request.user)
                # Don't call update_streak() - just let the profile exist
                # You can add streak logic here later if needed
            except Exception:
                pass
        
        return response

class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                profile, created = UserProfile.objects.get_or_create(user=request.user)
                timezone.activate(pytz.timezone(profile.timezone))
            except (UserProfile.DoesNotExist, pytz.UnknownTimeZoneError):
                timezone.activate(pytz.timezone('Africa/Nairobi'))
        else:
            timezone.activate(pytz.timezone('Africa/Nairobi'))
        
        response = self.get_response(request)
        timezone.deactivate()
        return response