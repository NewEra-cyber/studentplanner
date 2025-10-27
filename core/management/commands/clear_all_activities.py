from django.core.management.base import BaseCommand
from core.models import Schedule, JKUATTimetable, UserTimetable, Task, ProgressTracker

class Command(BaseCommand):
    help = 'Clear all activities, timetables, tasks and progress to start fresh'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            help='Clear activities for specific username (optional)',
        )
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Skip confirmation prompt',
        )

    def handle(self, *args, **options):
        username = options.get('user')
        confirm = options.get('confirm')
        
        if username:
            from django.contrib.auth.models import User
            try:
                user = User.objects.get(username=username)
                users = [user]
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'User "{username}" not found!')
                )
                return
        else:
            # Clear for all users
            users = None
        
        if not confirm:
            if users:
                self.stdout.write(
                    self.style.WARNING(f'This will delete ALL activities for user: {username}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('This will delete ALL activities for ALL users!')
                )
            
            self.stdout.write(
                self.style.WARNING('The following will be deleted:')
            )
            self.stdout.write('  • All Schedule entries')
            self.stdout.write('  • All JKUATTimetable entries') 
            self.stdout.write('  • All UserTimetable entries')
            self.stdout.write('  • All Tasks')
            self.stdout.write('  • All ProgressTracker entries')
            
            confirm_input = input('Are you sure? (yes/no): ')
            if confirm_input.lower() not in ['yes', 'y']:
                self.stdout.write(self.style.WARNING('Operation cancelled.'))
                return

        # Delete activities
        if users:
            schedule_count = Schedule.objects.filter(user__in=users).delete()[0]
            jkuat_count = JKUATTimetable.objects.filter(user__in=users).delete()[0]
            user_timetable_count = UserTimetable.objects.filter(user__in=users).delete()[0]
            task_count = Task.objects.filter(user__in=users).delete()[0]
            progress_count = ProgressTracker.objects.filter(user__in=users).delete()[0]
        else:
            schedule_count = Schedule.objects.all().delete()[0]
            jkuat_count = JKUATTimetable.objects.all().delete()[0]
            user_timetable_count = UserTimetable.objects.all().delete()[0]
            task_count = Task.objects.all().delete()[0]
            progress_count = ProgressTracker.objects.all().delete()[0]

        self.stdout.write(
            self.style.SUCCESS(f'✅ Successfully cleared all activities!')
        )
        self.stdout.write(f'📋 Deleted {schedule_count} schedule entries')
        self.stdout.write(f'🏫 Deleted {jkuat_count} JKUAT timetable entries')
        self.stdout.write(f'📅 Deleted {user_timetable_count} user timetable entries')
        self.stdout.write(f'✅ Deleted {task_count} tasks')
        self.stdout.write(f'📊 Deleted {progress_count} progress entries')
        self.stdout.write(
            self.style.SUCCESS('🎯 You now have a clean slate to build your custom timetable!')
        )
        