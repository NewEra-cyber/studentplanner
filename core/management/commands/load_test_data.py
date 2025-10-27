from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Schedule
from datetime import time

class Command(BaseCommand):
    help = 'Load test schedule data'
    
    def handle(self, *args, **options):
        user = User.objects.get(username='Mark')
        
        # Clear existing
        Schedule.objects.filter(user=user).delete()
        
        # Add test schedule
        Schedule.objects.create(
            user=user,
            title='Morning Routine',
            day='Monday',
            start_time=time(6, 0),
            end_time=time(7, 0),
            activity_type='meal',
            location='Home'
        )
        
        Schedule.objects.create(
            user=user,
            title='Python Study Session',
            day='Monday', 
            start_time=time(9, 0),
            end_time=time(11, 0),
            activity_type='study',
            location='Library'
        )
        
        self.stdout.write(self.style.SUCCESS('✅ Test data loaded!'))