from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import SmartActivity, DailyFocus
from core.smart_scheduler import SmartScheduler
from datetime import time

class Command(BaseCommand):
    help = 'Initialize the smart gentleman routine for a user'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            required=True,
            help='Username to initialize routine for',
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset existing routine before creating new one',
        )

    def handle(self, *args, **options):
        username = options['user']
        reset = options['reset']
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User "{username}" not found!')
            )
            return

        # Create user profile if it doesn't exist
        from core.models import UserProfile
        profile, created = UserProfile.objects.get_or_create(user=user)
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created profile for {username}')
            )

        if reset:
            # Clear existing smart activities
            deleted_count = SmartActivity.objects.filter(user=user).delete()[0]
            self.stdout.write(
                self.style.WARNING(f'Deleted {deleted_count} existing activities')
            )

        # Check if routine already exists
        existing_count = SmartActivity.objects.filter(user=user).count()
        if existing_count > 0 and not reset:
            self.stdout.write(
                self.style.WARNING(f'Routine already exists for {username} ({existing_count} activities)')
            )
            confirm = input('Continue and create duplicate activities? (yes/no): ')
            if confirm.lower() not in ['yes', 'y']:
                self.stdout.write(self.style.WARNING('Operation cancelled.'))
                return

        # Initialize the smart scheduler
        scheduler = SmartScheduler(user)
        
        # Create the gentleman routine
        created_count = scheduler.initialize_gentleman_routine()
        
        # Create daily focus quotes
        focus_count = self.create_daily_focus_quotes()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Successfully created {created_count} smart activities '
                f'and {focus_count} focus quotes for {username}!'
            )
        )
        self.stdout.write(
            self.style.SUCCESS('🎯 Your gentleman routine is now active!')
        )
        self.stdout.write(
            self.style.SUCCESS('📚 The system will auto-adjust when you add timetable entries.')
        )

    def create_daily_focus_quotes(self):
        """Create motivational focus quotes"""
        quotes = [
            {
                'quote': 'The key to success is to focus on goals, not obstacles.',
                'author': 'Unknown',
                'category': 'morning_routine'
            },
            {
                'quote': 'Discipline is choosing between what you want now and what you want most.',
                'author': 'Abraham Lincoln',
                'category': 'fitness'
            },
            {
                'quote': 'Your body is a temple, but only if you treat it as one.',
                'author': 'Astrid Alauda',
                'category': 'meal'
            },
            {
                'quote': 'Education is the most powerful weapon which you can use to change the world.',
                'author': 'Nelson Mandela',
                'category': 'academic'
            },
            {
                'quote': 'The only person you are destined to become is the person you decide to be.',
                'author': 'Ralph Waldo Emerson',
                'category': 'personal'
            },
            {
                'quote': 'The greatest gift you can give someone is your time and attention.',
                'author': 'Unknown',
                'category': 'social'
            },
            {
                'quote': 'Without reflection, we go blindly on our way, creating more unintended consequences.',
                'author': 'Margaret J. Wheatley',
                'category': 'reflection'
            },
            {
                'quote': 'Sleep is the best meditation.',
                'author': 'Dalai Lama',
                'category': 'rest'
            },
            {
                'quote': 'Morning is wonderful. Its only drawback is that it comes at such an inconvenient time of day.',
                'author': 'Glen Cook',
                'category': 'morning_routine'
            },
            {
                'quote': 'The only bad workout is the one that didn\'t happen.',
                'author': 'Unknown',
                'category': 'fitness'
            }
        ]
        
        created_count = 0
        for quote_data in quotes:
            DailyFocus.objects.get_or_create(
                quote=quote_data['quote'],
                defaults={
                    'author': quote_data['author'],
                    'category': quote_data['category']
                }
            )
            created_count += 1
        
        return created_count