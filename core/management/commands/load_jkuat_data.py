from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Schedule
from datetime import time

class Command(BaseCommand):
    help = 'Load JKUAT timetable + Beast Mode Schedule'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Loading Beast Mode Schedule...'))
        
        user = User.objects.filter(username__in=['Mark', 'mark', 'admin']).first()
        if not user:
            user, created = User.objects.get_or_create(
                username='mark',
                defaults={'email': 'mark@jkuat.ac.ke', 'first_name': 'Mark'}
            )
        
        self.stdout.write(self.style.SUCCESS(f'User: {user.username}'))
        
        # Clear existing
        Schedule.objects.filter(user=user).delete()
        
        complete_schedule = [
            # Morning Routines
            {'day': 'Monday', 'start_time': time(5, 30), 'end_time': time(6, 0), 
             'title': 'Morning Meditation', 'activity_type': 'chore', 'location': 'Home'},
            {'day': 'Tuesday', 'start_time': time(5, 30), 'end_time': time(6, 0), 
             'title': 'Morning Meditation', 'activity_type': 'chore', 'location': 'Home'},
            
            # Workouts
            {'day': 'Monday', 'start_time': time(6, 0), 'end_time': time(6, 30), 
             'title': 'Morning Workout', 'activity_type': 'workout', 'location': 'Home'},
            {'day': 'Tuesday', 'start_time': time(6, 0), 'end_time': time(6, 30), 
             'title': 'Morning Workout', 'activity_type': 'workout', 'location': 'Home'},
            {'day': 'Wednesday', 'start_time': time(6, 0), 'end_time': time(6, 30), 
             'title': 'Morning Workout', 'activity_type': 'workout', 'location': 'Home'},
            {'day': 'Thursday', 'start_time': time(6, 0), 'end_time': time(6, 30), 
             'title': 'Morning Workout', 'activity_type': 'workout', 'location': 'Home'},
            {'day': 'Friday', 'start_time': time(6, 0), 'end_time': time(6, 30), 
             'title': 'Morning Workout', 'activity_type': 'workout', 'location': 'Home'},
            
            # Meals
            {'day': 'Monday', 'start_time': time(7, 0), 'end_time': time(8, 0), 
             'title': 'Breakfast', 'activity_type': 'meal', 'location': 'Home'},
            {'day': 'Tuesday', 'start_time': time(9, 0), 'end_time': time(10, 0), 
             'title': 'Breakfast', 'activity_type': 'meal', 'location': 'Cafeteria'},
            {'day': 'Monday', 'start_time': time(13, 0), 'end_time': time(14, 0), 
             'title': 'Lunch', 'activity_type': 'meal', 'location': 'Cafeteria'},
            {'day': 'Tuesday', 'start_time': time(13, 0), 'end_time': time(14, 0), 
             'title': 'Lunch', 'activity_type': 'meal', 'location': 'Cafeteria'},
            {'day': 'Monday', 'start_time': time(19, 0), 'end_time': time(20, 0), 
             'title': 'Dinner', 'activity_type': 'meal', 'location': 'Home'},
            
            # Study Sessions
            {'day': 'Monday', 'start_time': time(20, 0), 'end_time': time(21, 30), 
             'title': 'OOP Study Session', 'activity_type': 'study', 'location': 'Library'},
            {'day': 'Tuesday', 'start_time': time(20, 0), 'end_time': time(21, 30), 
             'title': 'DBMS Study Session', 'activity_type': 'study', 'location': 'Library'},
            
            # JKUAT Classes
            {'day': 'Monday', 'start_time': time(10, 0), 'end_time': time(13, 0), 
             'title': 'ICS 2203 - Web App Development', 'activity_type': 'lab', 'location': 'Lab 7'},
            {'day': 'Monday', 'start_time': time(14, 0), 'end_time': time(17, 0), 
             'title': 'ICS 2302 - Software Engineering', 'activity_type': 'lab', 'location': 'Lab 7'},
            {'day': 'Monday', 'start_time': time(17, 0), 'end_time': time(19, 0), 
             'title': 'BIT 2214 - OOP Systems', 'activity_type': 'lecture', 'location': 'Hall 2'},
            
            {'day': 'Tuesday', 'start_time': time(7, 0), 'end_time': time(9, 0), 
             'title': 'ICS 2206 - Database Systems', 'activity_type': 'lab', 'location': 'Lab 6'},
            {'day': 'Tuesday', 'start_time': time(10, 0), 'end_time': time(13, 0), 
             'title': 'SMA 2101 - Calculus 1', 'activity_type': 'lecture', 'location': 'LH1'},
            {'day': 'Tuesday', 'start_time': time(14, 0), 'end_time': time(17, 0), 
             'title': 'ICS 2104 - OOP Programming', 'activity_type': 'lab', 'location': 'Lab 7'},
            
            {'day': 'Wednesday', 'start_time': time(7, 0), 'end_time': time(10, 0), 
             'title': 'BIT 2223 - Mobile Computing', 'activity_type': 'lecture', 'location': 'CTC 207'},
            {'day': 'Wednesday', 'start_time': time(11, 0), 'end_time': time(13, 0), 
             'title': 'ICS 2203 - Web App Development', 'activity_type': 'lecture', 'location': 'LH1'},
            
            {'day': 'Thursday', 'start_time': time(7, 0), 'end_time': time(10, 0), 
             'title': 'ICS 2206 - Database Systems', 'activity_type': 'lab', 'location': 'Lab 6'},
            {'day': 'Thursday', 'start_time': time(10, 0), 'end_time': time(12, 0), 
             'title': 'ICS 2104 - OOP Programming', 'activity_type': 'lab', 'location': 'Lab 7'},
            
            {'day': 'Friday', 'start_time': time(7, 0), 'end_time': time(10, 0), 
             'title': 'BIT 2214 - OOP Systems', 'activity_type': 'lab', 'location': 'Lab 5'},
            {'day': 'Friday', 'start_time': time(11, 0), 'end_time': time(13, 0), 
             'title': 'ICS 2302 - Software Engineering', 'activity_type': 'lecture', 'location': 'CTC 207'},
        ]
        
        activities_created = 0
        for item in complete_schedule:
            try:
                Schedule.objects.create(
                    user=user,
                    day=item['day'],
                    start_time=item['start_time'],
                    end_time=item['end_time'],
                    title=item['title'],
                    activity_type=item['activity_type'],
                    location=item['location'],
                )
                activities_created += 1
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Could not create: {item["title"]} - {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'Loaded {activities_created} activities!'))

    def get_color_for_activity(self, activity_type):
        color_map = {
            'lecture': '#3B82F6',
            'lab': '#8B5CF6',
            'study': '#10B981',
            'workout': '#EF4444',
            'meal': '#84CC16',
        }
        return color_map.get(activity_type, '#3B82F6')