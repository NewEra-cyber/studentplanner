from django.core.management.base import BaseCommand
from core.models import JKUATTimetable, User
from datetime import time

class Command(BaseCommand):
    help = 'Load JKUAT timetable data'
    
    def handle(self, *args, **options):
        user = User.objects.first()  # Or specify your user
        
        timetable_data = [
            # MONDAY
            {'day': 'Monday', 'start_time': time(10, 0), 'end_time': time(13, 0), 
             'course_code': 'ICS 2203', 'course_name': 'Web Application Development I', 'venue': 'LAB 7'},
            {'day': 'Monday', 'start_time': time(14, 0), 'end_time': time(17, 0), 
             'course_code': 'ICS 2302', 'course_name': 'Software Engineering I', 'venue': 'LAB 7'},
            {'day': 'Monday', 'start_time': time(17, 0), 'end_time': time(19, 0), 
             'course_code': 'BIT 2214', 'course_name': 'Object Oriented System and Design', 'venue': 'LEC HALL 2'},
            
            # TUESDAY
            {'day': 'Tuesday', 'start_time': time(7, 0), 'end_time': time(9, 0), 
             'course_code': 'ICS 2206', 'course_name': 'Introduction to Database Management Systems', 'venue': 'LAB 6'},
            {'day': 'Tuesday', 'start_time': time(10, 0), 'end_time': time(13, 0), 
             'course_code': 'SMA 2101', 'course_name': 'Calculus I', 'venue': 'CTC LH1'},
            {'day': 'Tuesday', 'start_time': time(14, 0), 'end_time': time(17, 0), 
             'course_code': 'ICS 2104', 'course_name': 'Object Oriented Programming I', 'venue': 'LAB 7'},
            {'day': 'Tuesday', 'start_time': time(17, 0), 'end_time': time(19, 0), 
             'course_code': 'BIT 2324', 'course_name': 'Geographical Information Systems', 'venue': 'LEC HALL 3'},
            
            # WEDNESDAY
            {'day': 'Wednesday', 'start_time': time(7, 0), 'end_time': time(10, 0), 
             'course_code': 'BIT 2223', 'course_name': 'Mobile Computing', 'venue': 'CTC 207'},
            {'day': 'Wednesday', 'start_time': time(11, 0), 'end_time': time(13, 0), 
             'course_code': 'ICS 2203', 'course_name': 'Web Application Development I', 'venue': 'LH 1'},
            
            # THURSDAY
            {'day': 'Thursday', 'start_time': time(7, 0), 'end_time': time(10, 0), 
             'course_code': 'ICS 2206', 'course_name': 'Introduction to Database Management Systems', 'venue': 'LAB 6'},
            {'day': 'Thursday', 'start_time': time(10, 0), 'end_time': time(12, 0), 
             'course_code': 'ICS 2104', 'course_name': 'Object Oriented Programming I', 'venue': 'LAB 7'},
            {'day': 'Thursday', 'start_time': time(14, 0), 'end_time': time(17, 0), 
             'course_code': 'BIT 2324', 'course_name': 'Geographical Information Systems', 'venue': 'LAB 4'},
            
            # FRIDAY
            {'day': 'Friday', 'start_time': time(7, 0), 'end_time': time(10, 0), 
             'course_code': 'BIT 2214', 'course_name': 'Object Oriented System and Design', 'venue': 'LAB 5'},
            {'day': 'Friday', 'start_time': time(11, 0), 'end_time': time(13, 0), 
             'course_code': 'ICS 2302', 'course_name': 'Software Engineering I', 'venue': 'CTC 207'},
            {'day': 'Friday', 'start_time': time(13, 0), 'end_time': time(15, 0), 
             'course_code': 'BIT 2223', 'course_name': 'Mobile Computing', 'venue': 'CTC 207'},
        ]
        
        for data in timetable_data:
            JKUATTimetable.objects.get_or_create(user=user, **data)
        
        self.stdout.write(self.style.SUCCESS('Successfully loaded JKUAT timetable data'))