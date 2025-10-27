from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import ResourceCategory, ActivityResource, SmartActivity, DailyFocus
from datetime import time

class Command(BaseCommand):
    help = 'Populate the database with comprehensive resource categories, resources, and Mark\'s God-Centered Routine'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default=None,
            help='Username to initialize God-Centered Routine for (optional)'
        )
        parser.add_argument(
            '--skip-resources',
            action='store_true',
            help='Skip creating resources, only create routine'
        )
        parser.add_argument(
            '--skip-routine',
            action='store_true',
            help='Skip creating routine, only create resources'
        )

    def handle(self, *args, **options):
        username = options.get('username')
        skip_resources = options.get('skip_resources', False)
        skip_routine = options.get('skip_routine', False)
        
        # Create Resources
        if not skip_resources:
            self.create_resources()
        
        # Create God-Centered Routine
        if not skip_routine and username:
            self.create_god_centered_routine(username)
        elif not skip_routine and not username:
            self.stdout.write(
                self.style.WARNING('\n⚠️  Skipping routine creation. Use --username=YOUR_USERNAME to create routine.')
            )
        
        self.stdout.write(self.style.SUCCESS('\n✅ All done!\n'))

    def create_resources(self):
        """Create resource categories and resources"""
        self.stdout.write('Creating comprehensive resource database...')
        
        # Clear existing data
        ActivityResource.objects.all().delete()
        ResourceCategory.objects.all().delete()
        
        # Create categories
        categories_data = [
            {
                'name': '🎮 Games & Entertainment',
                'description': 'Fun games and entertainment for breaks and relaxation',
                'icon': '🎮',
                'color': '#FF6B6B'
            },
            {
                'name': '📚 Learning Platforms',
                'description': 'Online learning platforms and educational resources',
                'icon': '📚',
                'color': '#4ECDC4'
            },
            {
                'name': '💻 Programming & Development',
                'description': 'Coding resources, tools, and development platforms',
                'icon': '💻',
                'color': '#45B7D1'
            },
            {
                'name': '🔧 Productivity Tools',
                'description': 'Tools to boost productivity and organization',
                'icon': '🔧',
                'color': '#96CEB4'
            },
            {
                'name': '📖 Study Resources',
                'description': 'Study aids, flashcards, and academic resources',
                'icon': '📖',
                'color': '#FFEAA7'
            },
            {
                'name': '🎵 Music & Focus',
                'description': 'Music and audio tools for concentration',
                'icon': '🎵',
                'color': '#DDA0DD'
            },
            {
                'name': '🧠 Health & Fitness',
                'description': 'Health, fitness, and mental wellness resources',
                'icon': '🧠',
                'color': '#98D8C8'
            },
            {
                'name': '📱 Social & Communication',
                'description': 'Social media and communication platforms',
                'icon': '📱',
                'color': '#F7DC6F'
            },
            {
                'name': '🎥 Video & Media',
                'description': 'Video streaming and media platforms',
                'icon': '🎥',
                'color': '#BB8FCE'
            },
            {
                'name': '📰 News & Information',
                'description': 'News outlets and information sources',
                'icon': '📰',
                'color': '#85C1E9'
            },
            {
                'name': '🛒 Shopping & Services',
                'description': 'Online shopping and service platforms',
                'icon': '🛒',
                'color': '#F8C471'
            },
            {
                'name': '💼 JKUAT Specific',
                'description': 'JKUAT university resources and portals',
                'icon': '💼',
                'color': '#A569BD'
            }
        ]
        
        # Create categories and resources
        for cat_data in categories_data:
            category = ResourceCategory.objects.create(
                name=cat_data['name'],
                description=cat_data['description'],
                icon=cat_data['icon'],
                color=cat_data['color']
            )
            self.stdout.write(f'Created category: {category.name}')
            
            # Create resources for this category
            self.create_resources_for_category(category)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Successfully created {ResourceCategory.objects.count()} categories and {ActivityResource.objects.count()} resources!\n'
            )
        )
    
    def create_resources_for_category(self, category):
        """Create resources for a specific category"""
        resources_data = []
        
        if category.name == '🎮 Games & Entertainment':
            resources_data = [
                {'name': 'Cool Math Games', 'description': 'Fun educational games for brain breaks', 'url': 'https://www.coolmathgames.com/', 'resource_type': 'website', 'activity_type': 'break', 'icon': '🎯', 'is_free': True},
                {'name': 'Chess.com', 'description': 'Play chess online with players worldwide', 'url': 'https://www.chess.com/', 'resource_type': 'website', 'activity_type': 'break', 'icon': '♟️', 'is_free': True},
                {'name': 'Lichess', 'description': 'Free and open source chess platform', 'url': 'https://lichess.org/', 'resource_type': 'website', 'activity_type': 'break', 'icon': '🏆', 'is_free': True},
                {'name': 'Tetris', 'description': 'Classic tetris game online', 'url': 'https://tetris.com/play-tetris', 'resource_type': 'website', 'activity_type': 'break', 'icon': '🧩', 'is_free': True},
                {'name': 'Sudoku', 'description': 'Daily sudoku puzzles', 'url': 'https://sudoku.com/', 'resource_type': 'website', 'activity_type': 'break', 'icon': '9️⃣', 'is_free': True}
            ]
        elif category.name == '📚 Learning Platforms':
            resources_data = [
                {'name': 'YouTube Learning', 'description': 'Educational content across all subjects', 'url': 'https://www.youtube.com/', 'resource_type': 'website', 'activity_type': 'study', 'icon': '📺', 'is_free': True},
                {'name': 'Coursera', 'description': 'Online courses from top universities', 'url': 'https://www.coursera.org/', 'resource_type': 'website', 'activity_type': 'study', 'icon': '🎓', 'is_free': False},
                {'name': 'edX', 'description': 'University courses from MIT, Harvard, etc.', 'url': 'https://www.edx.org/', 'resource_type': 'website', 'activity_type': 'study', 'icon': '🏛️', 'is_free': True},
                {'name': 'Khan Academy', 'description': 'Free online courses and lessons', 'url': 'https://www.khanacademy.org/', 'resource_type': 'website', 'activity_type': 'study', 'icon': '📖', 'is_free': True},
                {'name': 'Udemy', 'description': 'Online courses on various topics', 'url': 'https://www.udemy.com/', 'resource_type': 'website', 'activity_type': 'skill', 'icon': '💼', 'is_free': False}
            ]
        elif category.name == '💻 Programming & Development':
            resources_data = [
                {'name': 'GitHub', 'description': 'Code hosting and collaboration', 'url': 'https://github.com/', 'resource_type': 'website', 'activity_type': 'project', 'icon': '🐙', 'is_free': True},
                {'name': 'Stack Overflow', 'description': 'Q&A for programmers', 'url': 'https://stackoverflow.com/', 'resource_type': 'website', 'activity_type': 'project', 'icon': '🔍', 'is_free': True},
                {'name': 'W3Schools', 'description': 'Web development tutorials', 'url': 'https://www.w3schools.com/', 'resource_type': 'website', 'activity_type': 'study', 'icon': '🌐', 'is_free': True},
                {'name': 'MDN Web Docs', 'description': 'Web technology documentation', 'url': 'https://developer.mozilla.org/', 'resource_type': 'website', 'activity_type': 'study', 'icon': '📄', 'is_free': True},
                {'name': 'LeetCode', 'description': 'Coding interview preparation', 'url': 'https://leetcode.com/', 'resource_type': 'website', 'activity_type': 'study', 'icon': '💡', 'is_free': True}
            ]
        elif category.name == '🔧 Productivity Tools':
            resources_data = [
                {'name': 'Notion', 'description': 'All-in-one workspace for notes and tasks', 'url': 'https://www.notion.so/', 'resource_type': 'tool', 'activity_type': 'study', 'icon': '📝', 'is_free': True},
                {'name': 'Trello', 'description': 'Project management with boards and cards', 'url': 'https://trello.com/', 'resource_type': 'tool', 'activity_type': 'project', 'icon': '📋', 'is_free': True},
                {'name': 'Google Drive', 'description': 'Cloud storage and collaboration', 'url': 'https://drive.google.com/', 'resource_type': 'tool', 'activity_type': 'study', 'icon': '☁️', 'is_free': True},
                {'name': 'Grammarly', 'description': 'Writing assistant and grammar checker', 'url': 'https://www.grammarly.com/', 'resource_type': 'tool', 'activity_type': 'study', 'icon': '✍️', 'is_free': True},
                {'name': 'Canva', 'description': 'Graphic design platform', 'url': 'https://www.canva.com/', 'resource_type': 'tool', 'activity_type': 'project', 'icon': '🎨', 'is_free': True}
            ]
        elif category.name == '📖 Study Resources':
            resources_data = [
                {'name': 'Quizlet', 'description': 'Flashcards and study tools', 'url': 'https://quizlet.com/', 'resource_type': 'website', 'activity_type': 'study', 'icon': '📚', 'is_free': True},
                {'name': 'Anki', 'description': 'Spaced repetition flashcards', 'url': 'https://apps.ankiweb.net/', 'resource_type': 'tool', 'activity_type': 'study', 'icon': '🔄', 'is_free': True},
                {'name': 'Wolfram Alpha', 'description': 'Computational knowledge engine', 'url': 'https://www.wolframalpha.com/', 'resource_type': 'website', 'activity_type': 'study', 'icon': '🧮', 'is_free': True},
                {'name': 'Google Scholar', 'description': 'Academic research papers', 'url': 'https://scholar.google.com/', 'resource_type': 'website', 'activity_type': 'study', 'icon': '📖', 'is_free': True},
                {'name': 'Z-Library', 'description': 'Free ebook library', 'url': 'https://z-lib.org/', 'resource_type': 'website', 'activity_type': 'study', 'icon': '📚', 'is_free': True}
            ]
        elif category.name == '🎵 Music & Focus':
            resources_data = [
                {'name': 'Spotify', 'description': 'Music streaming for focus', 'url': 'https://open.spotify.com/', 'resource_type': 'app', 'activity_type': 'study', 'icon': '🎵', 'is_free': True},
                {'name': 'YouTube Music', 'description': 'Music and audio streaming', 'url': 'https://music.youtube.com/', 'resource_type': 'app', 'activity_type': 'study', 'icon': '🎶', 'is_free': True},
                {'name': 'Brain.fm', 'description': 'Focus-enhancing music', 'url': 'https://www.brain.fm/', 'resource_type': 'app', 'activity_type': 'study', 'icon': '🧠', 'is_free': False},
                {'name': 'Focus@Will', 'description': 'Productivity music service', 'url': 'https://www.focusatwill.com/', 'resource_type': 'app', 'activity_type': 'study', 'icon': '🎧', 'is_free': False},
                {'name': 'Lo-fi Girl', 'description': '24/7 lo-fi study music', 'url': 'https://www.youtube.com/c/LofiGirl', 'resource_type': 'website', 'activity_type': 'study', 'icon': '🌙', 'is_free': True}
            ]
        elif category.name == '🧠 Health & Fitness':
            resources_data = [
                {'name': 'Nike Training Club', 'description': 'Free workout routines', 'url': 'https://www.nike.com/ntc-app', 'resource_type': 'app', 'activity_type': 'workout', 'icon': '👟', 'is_free': True},
                {'name': 'MyFitnessPal', 'description': 'Calorie and nutrition tracking', 'url': 'https://www.myfitnesspal.com/', 'resource_type': 'app', 'activity_type': 'meal', 'icon': '🍎', 'is_free': True},
                {'name': 'Headspace', 'description': 'Meditation and mindfulness', 'url': 'https://www.headspace.com/', 'resource_type': 'app', 'activity_type': 'break', 'icon': '🧘', 'is_free': False},
                {'name': 'Calm', 'description': 'Meditation and sleep app', 'url': 'https://www.calm.com/', 'resource_type': 'app', 'activity_type': 'break', 'icon': '🌊', 'is_free': False},
                {'name': 'Strava', 'description': 'Fitness and running tracker', 'url': 'https://www.strava.com/', 'resource_type': 'app', 'activity_type': 'workout', 'icon': '🏃', 'is_free': True}
            ]
        elif category.name == '📱 Social & Communication':
            resources_data = [
                {'name': 'WhatsApp', 'description': 'Messaging and calls', 'url': 'https://web.whatsapp.com/', 'resource_type': 'app', 'activity_type': 'relationship', 'icon': '💬', 'is_free': True},
                {'name': 'Discord', 'description': 'Community and group chats', 'url': 'https://discord.com/', 'resource_type': 'app', 'activity_type': 'relationship', 'icon': '🎮', 'is_free': True},
                {'name': 'Zoom', 'description': 'Video conferencing', 'url': 'https://zoom.us/', 'resource_type': 'app', 'activity_type': 'meeting', 'icon': '📹', 'is_free': True},
                {'name': 'Google Meet', 'description': 'Video meetings', 'url': 'https://meet.google.com/', 'resource_type': 'app', 'activity_type': 'meeting', 'icon': '🎥', 'is_free': True},
                {'name': 'Slack', 'description': 'Team communication', 'url': 'https://slack.com/', 'resource_type': 'app', 'activity_type': 'meeting', 'icon': '💼', 'is_free': True}
            ]
        elif category.name == '🎥 Video & Media':
            resources_data = [
                {'name': 'YouTube', 'description': 'Video streaming platform', 'url': 'https://www.youtube.com/', 'resource_type': 'website', 'activity_type': 'break', 'icon': '📺', 'is_free': True},
                {'name': 'Netflix', 'description': 'Movie and TV streaming', 'url': 'https://www.netflix.com/', 'resource_type': 'website', 'activity_type': 'break', 'icon': '🎬', 'is_free': False},
                {'name': 'Disney+', 'description': 'Disney, Marvel, Star Wars content', 'url': 'https://www.disneyplus.com/', 'resource_type': 'website', 'activity_type': 'break', 'icon': '🏰', 'is_free': False},
                {'name': 'Twitch', 'description': 'Live streaming platform', 'url': 'https://www.twitch.tv/', 'resource_type': 'website', 'activity_type': 'break', 'icon': '🟣', 'is_free': True},
                {'name': 'TikTok', 'description': 'Short form video platform', 'url': 'https://www.tiktok.com/', 'resource_type': 'app', 'activity_type': 'break', 'icon': '🎵', 'is_free': True}
            ]
        elif category.name == '📰 News & Information':
            resources_data = [
                {'name': 'BBC News', 'description': 'International news coverage', 'url': 'https://www.bbc.com/news', 'resource_type': 'website', 'activity_type': 'break', 'icon': '🇬🇧', 'is_free': True},
                {'name': 'CNN', 'description': 'News and current events', 'url': 'https://edition.cnn.com/', 'resource_type': 'website', 'activity_type': 'break', 'icon': '📰', 'is_free': True},
                {'name': 'Al Jazeera', 'description': 'Global news network', 'url': 'https://www.aljazeera.com/', 'resource_type': 'website', 'activity_type': 'break', 'icon': '🌍', 'is_free': True},
                {'name': 'Reuters', 'description': 'International news agency', 'url': 'https://www.reuters.com/', 'resource_type': 'website', 'activity_type': 'break', 'icon': '📊', 'is_free': True},
                {'name': 'TechCrunch', 'description': 'Technology news', 'url': 'https://techcrunch.com/', 'resource_type': 'website', 'activity_type': 'break', 'icon': '💻', 'is_free': True}
            ]
        elif category.name == '🛒 Shopping & Services':
            resources_data = [
                {'name': 'Amazon', 'description': 'Online shopping marketplace', 'url': 'https://www.amazon.com/', 'resource_type': 'website', 'activity_type': 'break', 'icon': '📦', 'is_free': True},
                {'name': 'Jumia', 'description': 'African online marketplace', 'url': 'https://www.jumia.co.ke/', 'resource_type': 'website', 'activity_type': 'break', 'icon': '🛍️', 'is_free': True},
                {'name': 'eBay', 'description': 'Online auctions and shopping', 'url': 'https://www.ebay.com/', 'resource_type': 'website', 'activity_type': 'break', 'icon': '💰', 'is_free': True},
                {'name': 'AliExpress', 'description': 'International online retail', 'url': 'https://www.aliexpress.com/', 'resource_type': 'website', 'activity_type': 'break', 'icon': '🚢', 'is_free': True},
                {'name': 'Uber Eats', 'description': 'Food delivery service', 'url': 'https://www.ubereats.com/', 'resource_type': 'app', 'activity_type': 'meal', 'icon': '🍔', 'is_free': True}
            ]
        elif category.name == '💼 JKUAT Specific':
            resources_data = [
                {'name': 'JKUAT eLearning Portal', 'description': 'Official JKUAT online learning platform', 'url': 'https://elearning.jkuat.ac.ke/', 'resource_type': 'website', 'activity_type': 'lecture', 'icon': '🏫', 'is_free': True},
                {'name': 'JKUAT Library Portal', 'description': 'Digital library resources and databases', 'url': 'https://library.jkuat.ac.ke/', 'resource_type': 'website', 'activity_type': 'study', 'icon': '📚', 'is_free': True},
                {'name': 'JKUAT Student Portal', 'description': 'Student information and registration system', 'url': 'https://student.jkuat.ac.ke/', 'resource_type': 'website', 'activity_type': 'academic', 'icon': '🎓', 'is_free': True},
                {'name': 'JKUAT Past Papers', 'description': 'Repository of previous exam papers', 'url': 'https://repository.jkuat.ac.ke/', 'resource_type': 'website', 'activity_type': 'study', 'icon': '📝', 'is_free': True},
                {'name': 'JKUAT Website', 'description': 'Official university website', 'url': 'https://www.jkuat.ac.ke/', 'resource_type': 'website', 'activity_type': 'academic', 'icon': '🌐', 'is_free': True}
            ]
        
        # Create resources
        for resource_data in resources_data:
            ActivityResource.objects.create(category=category, **resource_data)
            self.stdout.write(f'  - Created resource: {resource_data["name"]}')

    def create_god_centered_routine(self, username):
        """Create Mark Munda's Ultimate God-Centered Student Routine FOR ALL DAYS"""
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'\n❌ User "{username}" does not exist. Please create the user first.'))
            return

        self.stdout.write(f'\n{"="*70}')
        self.stdout.write(f'🙏 Initializing God-Centered Routine for {user.username}...\n')

        # Clear existing smart activities for this user
        deleted_count = SmartActivity.objects.filter(user=user).delete()[0]
        if deleted_count > 0:
            self.stdout.write(f'Cleared {deleted_count} existing smart activities\n')

        # Days of the week
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        # Mark's Ultimate God-Centered Student Routine (template)
        routine_template = [
            {
                'title': '🙏 Morning Devotion & Gratitude',
                'category': 'morning_routine',
                'start_time': time(6, 0),
                'end_time': time(7, 0),
                'duration_minutes': 60,
                'priority_level': 1,
                'is_flexible': False,
                'shift_margin_minutes': 0,
                'min_duration_minutes': 45,
                'description': 'Prayer Corner - Home'
            },
            {
                'title': '🍳 Breakfast & Planning',
                'category': 'meal',
                'start_time': time(7, 0),
                'end_time': time(7, 20),
                'duration_minutes': 20,
                'priority_level': 2,
                'is_flexible': True,
                'shift_margin_minutes': 30,
                'min_duration_minutes': 10,
                'description': 'Dining Room - Home'
            },
            {
                'title': '🍱 Lunch Break',
                'category': 'meal',
                'start_time': time(13, 0),
                'end_time': time(13, 30),
                'duration_minutes': 30,
                'priority_level': 2,
                'is_flexible': True,
                'shift_margin_minutes': 120,
                'min_duration_minutes': 20,
                'description': 'Campus Cafeteria / Home'
            },
            {
                'title': '💕 Romance & Chilling',
                'category': 'relationship',
                'start_time': time(17, 0),
                'end_time': time(20, 0),
                'duration_minutes': 180,
                'priority_level': 2,
                'is_flexible': True,
                'shift_margin_minutes': 180,
                'min_duration_minutes': 60,
                'description': 'Quality Time - Flexible Location'
            },
            {
                'title': '💻 Coding & Projects',
                'category': 'personal',
                'start_time': time(20, 0),
                'end_time': time(22, 0),
                'duration_minutes': 120,
                'priority_level': 3,
                'is_flexible': True,
                'shift_margin_minutes': 120,
                'min_duration_minutes': 60,
                'description': 'Dev Station - Home'
            },
            {
                'title': '💪 Workout & Yoga',
                'category': 'fitness',
                'start_time': time(16, 0),
                'end_time': time(17, 0),
                'duration_minutes': 60,
                'priority_level': 2,
                'is_flexible': True,
                'shift_margin_minutes': 120,
                'min_duration_minutes': 30,
                'description': 'JKUAT Gym / Home'
            },
            {
                'title': '🍽️ Dinner & Wind-Down',
                'category': 'meal',
                'start_time': time(21, 0),
                'end_time': time(22, 0),
                'duration_minutes': 60,
                'priority_level': 2,
                'is_flexible': True,
                'shift_margin_minutes': 60,
                'min_duration_minutes': 30,
                'description': 'Kitchen - Home'
            },
            {
                'title': '✍️ Reflection & Prayer',
                'category': 'reflection',
                'start_time': time(22, 30),
                'end_time': time(23, 0),
                'duration_minutes': 30,
                'priority_level': 1,
                'is_flexible': False,
                'shift_margin_minutes': 0,
                'min_duration_minutes': 20,
                'description': 'Study Desk - Home'
            },
            {
                'title': '😴 Sleeping',
                'category': 'rest',
                'start_time': time(23, 0),
                'end_time': time(6, 0),
                'duration_minutes': 420,
                'priority_level': 1,
                'is_flexible': False,
                'shift_margin_minutes': 0,
                'min_duration_minutes': 360,
                'description': 'Bedroom - Home'
            },
        ]

        # Create activities for EACH day of the week
        created_count = 0
        for day in days_of_week:
            for activity_template in routine_template:
                activity_data = activity_template.copy()
                activity_data['day'] = day
                activity_data['user'] = user
                
                SmartActivity.objects.create(**activity_data)
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f'✅ Created {len(routine_template)} activities × 7 days = {created_count} total activities!\n'))
        self.stdout.write('='*70)
        self.stdout.write(self.style.SUCCESS(f'🎉 Successfully created {created_count} activities!'))
        self.stdout.write(self.style.SUCCESS('🙏 Mark Munda\'s Ultimate God-Centered Student Routine is now active!\n'))
        
        # Show sample of created activities
        self.stdout.write('Sample activities created:\n')
        for activity_template in routine_template:
            emoji = activity_template['title'].split()[0]
            title_without_emoji = ' '.join(activity_template['title'].split()[1:])
            location = activity_template['description']
            self.stdout.write(
                self.style.SUCCESS(
                    f'  {emoji} {title_without_emoji} '
                    f'({activity_template["start_time"].strftime("%H:%M")} - {activity_template["end_time"].strftime("%H:%M")}) @ {location}'
                )
            )
        
        # Create motivational quotes
        self.stdout.write('\n')
        self.create_daily_focus_quotes()
        
        self.stdout.write('='*70 + '\n')

    def create_daily_focus_quotes(self):
        """Create inspirational daily focus quotes"""
        self.stdout.write('Creating Daily Focus Quotes...\n')
        
        quotes_data = [
            {
                'quote': 'Faith anchors direction. Discipline sustains progress. Growth builds strength. Reflection renews purpose.',
                'author': 'Mark Munda',
                'category': 'morning_routine'
            },
            {
                'quote': 'Trust in the Lord with all your heart and lean not on your own understanding; in all your ways submit to him, and he will make your paths straight.',
                'author': 'Proverbs 3:5-6',
                'category': 'morning_routine'
            },
            {
                'quote': 'I can do all things through Christ who strengthens me.',
                'author': 'Philippians 4:13',
                'category': 'fitness'
            },
            {
                'quote': 'Whatever you do, work at it with all your heart, as working for the Lord, not for human masters.',
                'author': 'Colossians 3:23',
                'category': 'personal'
            },
            {
                'quote': 'Do not be anxious about anything, but in every situation, by prayer and petition, with thanksgiving, present your requests to God.',
                'author': 'Philippians 4:6',
                'category': 'reflection'
            },
            {
                'quote': 'Commit to the Lord whatever you do, and he will establish your plans.',
                'author': 'Proverbs 16:3',
                'category': 'personal'
            },
            {
                'quote': 'The fear of the Lord is the beginning of wisdom, and knowledge of the Holy One is understanding.',
                'author': 'Proverbs 9:10',
                'category': 'academic'
            },
            {
                'quote': 'For I know the plans I have for you, declares the Lord, plans to prosper you and not to harm you, plans to give you hope and a future.',
                'author': 'Jeremiah 29:11',
                'category': 'morning_routine'
            },
            {
                'quote': 'Be strong and courageous. Do not be afraid; do not be discouraged, for the Lord your God will be with you wherever you go.',
                'author': 'Joshua 1:9',
                'category': 'fitness'
            },
            {
                'quote': 'In all your ways acknowledge him, and he will make straight your paths.',
                'author': 'Proverbs 3:6',
                'category': 'personal'
            },
            {
                'quote': 'Love is patient, love is kind. It does not envy, it does not boast, it is not proud.',
                'author': '1 Corinthians 13:4',
                'category': 'relationship'
            },
            {
                'quote': 'Two are better than one, because they have a good return for their labor.',
                'author': 'Ecclesiastes 4:9',
                'category': 'relationship'
            },
        ]

        # Clear existing quotes
        DailyFocus.objects.all().delete()

        # Create new quotes
        for quote_data in quotes_data:
            DailyFocus.objects.create(**quote_data)
            author_display = quote_data['author'][:30] + '...' if len(quote_data['author']) > 30 else quote_data['author']
            self.stdout.write(f'  📖 Added quote from {author_display}')

        self.stdout.write(self.style.SUCCESS(f'\n✅ Created {len(quotes_data)} motivational quotes!\n'))