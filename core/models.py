from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime, time, timedelta
import uuid

class UserProfile(models.Model):
    THEME_CHOICES = [
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('auto', 'Auto'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    weight = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    height = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    course = models.CharField(max_length=200, blank=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    wake_up_time = models.TimeField(default='06:00:00')
    sleep_time = models.TimeField(default='23:30:00')
    current_phase = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(12)])
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default='light')
    timezone = models.CharField(max_length=50, default='Africa/Nairobi')
    streak_count = models.IntegerField(default=0)
    total_points = models.IntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

class SmartActivity(models.Model):
    """Smart self-adjusting activities for gentleman routine"""
    CATEGORY_CHOICES = [
        ('morning_routine', '🌅 Morning Routine'),
        ('fitness', '💪 Fitness'),
        ('meal', '🍽️ Meal'),
        ('academic', '📚 Academic'),
        ('personal', '🚀 Personal Development'),
        ('social', '❤️ Social'),
        ('reflection', '📊 Reflection'),
        ('rest', '😴 Rest'),
    ]
    
    PRIORITY_LEVELS = [
        (1, 'Fixed - Cannot Move'),
        (2, 'High Priority'),
        (3, 'Medium Priority'),
        (4, 'Flexible'),
    ]
    
    DAYS_OF_WEEK = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
        ('daily', 'Daily'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='smart_activities')
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    day = models.CharField(max_length=10, choices=DAYS_OF_WEEK, default='daily')
    start_time = models.TimeField()
    end_time = models.TimeField()
    duration_minutes = models.IntegerField(help_text="Activity duration in minutes")
    
    # Smart adjustment fields
    priority_level = models.IntegerField(choices=PRIORITY_LEVELS, default=3)
    is_flexible = models.BooleanField(default=True)
    shift_margin_minutes = models.IntegerField(default=30, help_text="How many minutes this activity can shift")
    min_duration_minutes = models.IntegerField(default=15, help_text="Minimum duration required")
    
    # Tracking
    original_start_time = models.TimeField(null=True, blank=True)
    last_adjusted = models.DateTimeField(null=True, blank=True)
    adjustment_count = models.IntegerField(default=0)
    
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'smart_activities'
        ordering = ['day', 'start_time']
    
    def __str__(self):
        return f"{self.day} {self.start_time} - {self.title}"
    
    def save(self, *args, **kwargs):
        # Calculate duration if not set
        if not self.duration_minutes and self.start_time and self.end_time:
            start_dt = datetime.combine(datetime.today(), self.start_time)
            end_dt = datetime.combine(datetime.today(), self.end_time)
            self.duration_minutes = int((end_dt - start_dt).total_seconds() / 60)
        
        # Store original time on first save
        if not self.original_start_time:
            self.original_start_time = self.start_time
            
        super().save(*args, **kwargs)
    
    @property
    def display_title(self):
        """Return title with emoji if not already present"""
        if any(emoji in self.title for emoji in ['🌅', '💪', '🍽️', '📚', '❤️', '🚀', '📊', '😴']):
            return self.title
        # Add emoji based on category
        emoji_map = {
            'morning_routine': '🌅 ',
            'fitness': '💪 ',
            'meal': '🍽️ ',
            'academic': '📚 ',
            'personal': '🚀 ',
            'social': '❤️ ',
            'reflection': '📊 ',
            'rest': '😴 '
        }
        return f"{emoji_map.get(self.category, '📝 ')}{self.title}"

class Schedule(models.Model):
    ACTIVITY_TYPES = [
        ('lecture', '📚 Lecture'),
        ('lab', '💻 Lab'),
        ('study', '📖 Study Block'),
        ('workout', '💪 Workout'),
        ('chore', '🧹 Chore'),
        ('relationship', '❤️ Relationship Time'),
        ('skill', '🚀 Skill Development'),
        ('meal', '🍽️ Meal'),
        ('review', '📊 Review'),
        ('project', '🔨 Project Work'),
        ('break', '☕ Break'),
        ('commute', '🚗 Commute'),
        ('meeting', '👥 Meeting'),
    ]
    
    DAYS_OF_WEEK = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='schedules')
    title = models.CharField(max_length=200)
    day = models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    location = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    
    is_flexible = models.BooleanField(default=False)
    preferred_time = models.CharField(max_length=20, choices=[
        ('morning', 'Morning (6AM-12PM)'),
        ('afternoon', 'Afternoon (12PM-5PM)'), 
        ('evening', 'Evening (5PM-9PM)'),
        ('night', 'Night (9PM-11PM)'),
        ('any', 'Any Time'),
    ], default='any')
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'schedules'
        ordering = ['day', 'start_time']
    
    def __str__(self):
        return f"{self.day} {self.start_time} - {self.title}"
    
    @property
    def display_title(self):
        """Return title with emoji based on activity type"""
        if any(emoji in self.title for emoji in ['📚', '💻', '📖', '💪', '🧹', '❤️', '🚀', '🍽️', '📊', '🔨', '☕', '🚗', '👥']):
            return self.title
        # Get emoji from activity type choices
        for choice in self.ACTIVITY_TYPES:
            if choice[0] == self.activity_type:
                return f"{choice[1].split(' ')[0]} {self.title}"
        return self.title

class UserTimetable(models.Model):
    """User's custom timetable for manual input"""
    DAY_CHOICES = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_timetable')
    day = models.CharField(max_length=10, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    unit_code = models.CharField(max_length=20)
    unit_name = models.CharField(max_length=200)
    venue = models.CharField(max_length=100, blank=True)
    activity_type = models.CharField(max_length=20, choices=Schedule.ACTIVITY_TYPES, default='lecture')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_timetable'
        ordering = ['day', 'start_time']
        unique_together = ['user', 'day', 'start_time', 'unit_code']
    
    def __str__(self):
        return f"{self.day} {self.start_time} - {self.unit_code}"
    
    @property
    def title(self):
        """Return formatted title with emoji"""
        return f"📚 {self.unit_code} - {self.unit_name}"
    
    @property
    def description(self):
        """Return venue as description"""
        return self.venue or "Class"
    
    @property
    def display_title(self):
        """Alias for title for template compatibility"""
        return self.title

class JKUATTimetable(models.Model):
    DAY_CHOICES = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='jkuat_timetable')
    day = models.CharField(max_length=10, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    course_code = models.CharField(max_length=20)
    course_name = models.CharField(max_length=200)
    venue = models.CharField(max_length=100)
    activity_type = models.CharField(max_length=20, choices=Schedule.ACTIVITY_TYPES, default='lecture')
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['day', 'start_time']
    
    def __str__(self):
        return f"{self.day} {self.start_time} - {self.course_code}"
    
    @property
    def title(self):
        """Return formatted title with emoji"""
        return f"📚 {self.course_code} - {self.course_name}"
    
    @property
    def description(self):
        """Return venue as description"""
        return self.venue or "Class"
    
    @property
    def display_title(self):
        """Alias for title for template compatibility"""
        return self.title

class Task(models.Model):
    PRIORITY_CHOICES = [
        ('low', '🔵 Low'),
        ('medium', '🟡 Medium'),
        ('high', '🔴 High'),
    ]
    
    STATUS_CHOICES = [
        ('todo', '📝 To Do'),
        ('in_progress', '🔄 In Progress'),
        ('completed', '✅ Completed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='todo')
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tasks'
        ordering = ['priority', 'due_date']
    
    def __str__(self):
        return self.title

class ProgressTracker(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress_entries')
    date = models.DateField(default=timezone.now)
    tasks_completed = models.IntegerField(default=0)
    study_hours = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)])
    productivity_score = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])
    consistency_score = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'progress_tracker'
        unique_together = ['user', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.user.username} - {self.date}"

class ResourceCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=10, default='📁')
    color = models.CharField(max_length=7, default='#3B82F6')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'resource_categories'
        verbose_name_plural = 'Resource Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @classmethod
    def create_default_categories_and_resources(cls):
        """Create comprehensive resource database with 300+ resources"""
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
        
        # Create categories
        for cat_data in categories_data:
            category, created = cls.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            if created:
                # Create resources for this category
                cls.create_resources_for_category(category)
    
    @classmethod
    def create_resources_for_category(cls, category):
        """Create resources for a specific category"""
        from core.models import ActivityResource
        
        resources_data = []
        
        if category.name == '🎮 Games & Entertainment':
            resources_data = [
                {
                    'name': 'Cool Math Games',
                    'description': 'Fun educational games for brain breaks',
                    'url': 'https://www.coolmathgames.com/',
                    'resource_type': 'website',
                    'activity_type': 'break',
                    'icon': '🎯',
                    'is_free': True
                },
                {
                    'name': 'Chess.com',
                    'description': 'Play chess online with players worldwide',
                    'url': 'https://www.chess.com/',
                    'resource_type': 'website',
                    'activity_type': 'break',
                    'icon': '♟️',
                    'is_free': True
                },
                {
                    'name': 'Lichess',
                    'description': 'Free and open source chess platform',
                    'url': 'https://lichess.org/',
                    'resource_type': 'website', 
                    'activity_type': 'break',
                    'icon': '🏆',
                    'is_free': True
                },
                {
                    'name': 'Tetris',
                    'description': 'Classic tetris game online',
                    'url': 'https://tetris.com/play-tetris',
                    'resource_type': 'website',
                    'activity_type': 'break',
                    'icon': '🧩',
                    'is_free': True
                },
                {
                    'name': 'Sudoku',
                    'description': 'Daily sudoku puzzles',
                    'url': 'https://sudoku.com/',
                    'resource_type': 'website',
                    'activity_type': 'break', 
                    'icon': '9️⃣',
                    'is_free': True
                }
            ]
        
        elif category.name == '📚 Learning Platforms':
            resources_data = [
                {
                    'name': 'YouTube Learning',
                    'description': 'Educational content across all subjects',
                    'url': 'https://www.youtube.com/',
                    'resource_type': 'website',
                    'activity_type': 'study',
                    'icon': '📺',
                    'is_free': True
                },
                {
                    'name': 'Coursera',
                    'description': 'Online courses from top universities',
                    'url': 'https://www.coursera.org/',
                    'resource_type': 'website',
                    'activity_type': 'study',
                    'icon': '🎓',
                    'is_free': False
                },
                {
                    'name': 'edX',
                    'description': 'University courses from MIT, Harvard, etc.',
                    'url': 'https://www.edx.org/',
                    'resource_type': 'website',
                    'activity_type': 'study',
                    'icon': '🏛️',
                    'is_free': True
                },
                {
                    'name': 'Khan Academy',
                    'description': 'Free online courses and lessons',
                    'url': 'https://www.khanacademy.org/',
                    'resource_type': 'website',
                    'activity_type': 'study',
                    'icon': '📖',
                    'is_free': True
                },
                {
                    'name': 'Udemy',
                    'description': 'Online courses on various topics',
                    'url': 'https://www.udemy.com/',
                    'resource_type': 'website',
                    'activity_type': 'skill',
                    'icon': '💼',
                    'is_free': False
                }
            ]
        
        elif category.name == '💻 Programming & Development':
            resources_data = [
                {
                    'name': 'GitHub',
                    'description': 'Code hosting and collaboration',
                    'url': 'https://github.com/',
                    'resource_type': 'website',
                    'activity_type': 'project',
                    'icon': '🐙',
                    'is_free': True
                },
                {
                    'name': 'Stack Overflow',
                    'description': 'Q&A for programmers',
                    'url': 'https://stackoverflow.com/',
                    'resource_type': 'website',
                    'activity_type': 'project',
                    'icon': '🔍',
                    'is_free': True
                },
                {
                    'name': 'W3Schools',
                    'description': 'Web development tutorials',
                    'url': 'https://www.w3schools.com/',
                    'resource_type': 'website',
                    'activity_type': 'study',
                    'icon': '🌐',
                    'is_free': True
                },
                {
                    'name': 'MDN Web Docs',
                    'description': 'Web technology documentation',
                    'url': 'https://developer.mozilla.org/',
                    'resource_type': 'website',
                    'activity_type': 'study',
                    'icon': '📄',
                    'is_free': True
                },
                {
                    'name': 'LeetCode',
                    'description': 'Coding interview preparation',
                    'url': 'https://leetcode.com/',
                    'resource_type': 'website',
                    'activity_type': 'study',
                    'icon': '💡',
                    'is_free': True
                }
            ]
        
        elif category.name == '🔧 Productivity Tools':
            resources_data = [
                {
                    'name': 'Notion',
                    'description': 'All-in-one workspace for notes and tasks',
                    'url': 'https://www.notion.so/',
                    'resource_type': 'tool',
                    'activity_type': 'study',
                    'icon': '📝',
                    'is_free': True
                },
                {
                    'name': 'Trello',
                    'description': 'Project management with boards and cards',
                    'url': 'https://trello.com/',
                    'resource_type': 'tool',
                    'activity_type': 'project',
                    'icon': '📋',
                    'is_free': True
                },
                {
                    'name': 'Google Drive',
                    'description': 'Cloud storage and collaboration',
                    'url': 'https://drive.google.com/',
                    'resource_type': 'tool',
                    'activity_type': 'study',
                    'icon': '☁️',
                    'is_free': True
                },
                {
                    'name': 'Grammarly',
                    'description': 'Writing assistant and grammar checker',
                    'url': 'https://www.grammarly.com/',
                    'resource_type': 'tool',
                    'activity_type': 'study',
                    'icon': '✍️',
                    'is_free': True
                },
                {
                    'name': 'Canva',
                    'description': 'Graphic design platform',
                    'url': 'https://www.canva.com/',
                    'resource_type': 'tool',
                    'activity_type': 'project',
                    'icon': '🎨',
                    'is_free': True
                }
            ]
        
        elif category.name == '📖 Study Resources':
            resources_data = [
                {
                    'name': 'Quizlet',
                    'description': 'Flashcards and study tools',
                    'url': 'https://quizlet.com/',
                    'resource_type': 'website',
                    'activity_type': 'study',
                    'icon': '📚',
                    'is_free': True
                },
                {
                    'name': 'Anki',
                    'description': 'Spaced repetition flashcards',
                    'url': 'https://apps.ankiweb.net/',
                    'resource_type': 'tool',
                    'activity_type': 'study',
                    'icon': '🔄',
                    'is_free': True
                },
                {
                    'name': 'Wolfram Alpha',
                    'description': 'Computational knowledge engine',
                    'url': 'https://www.wolframalpha.com/',
                    'resource_type': 'website',
                    'activity_type': 'study',
                    'icon': '🧮',
                    'is_free': True
                },
                {
                    'name': 'Google Scholar',
                    'description': 'Academic research papers',
                    'url': 'https://scholar.google.com/',
                    'resource_type': 'website',
                    'activity_type': 'study',
                    'icon': '📖',
                    'is_free': True
                },
                {
                    'name': 'Z-Library',
                    'description': 'Free ebook library',
                    'url': 'https://z-lib.org/',
                    'resource_type': 'website',
                    'activity_type': 'study',
                    'icon': '📚',
                    'is_free': True
                }
            ]
        
        elif category.name == '🎵 Music & Focus':
            resources_data = [
                {
                    'name': 'Spotify',
                    'description': 'Music streaming for focus',
                    'url': 'https://open.spotify.com/',
                    'resource_type': 'app',
                    'activity_type': 'study',
                    'icon': '🎵',
                    'is_free': True
                },
                {
                    'name': 'YouTube Music',
                    'description': 'Music and audio streaming',
                    'url': 'https://music.youtube.com/',
                    'resource_type': 'app',
                    'activity_type': 'study',
                    'icon': '🎶',
                    'is_free': True
                },
                {
                    'name': 'Brain.fm',
                    'description': 'Focus-enhancing music',
                    'url': 'https://www.brain.fm/',
                    'resource_type': 'app',
                    'activity_type': 'study',
                    'icon': '🧠',
                    'is_free': False
                },
                {
                    'name': 'Focus@Will',
                    'description': 'Productivity music service',
                    'url': 'https://www.focusatwill.com/',
                    'resource_type': 'app',
                    'activity_type': 'study',
                    'icon': '🎧',
                    'is_free': False
                },
                {
                    'name': 'Lo-fi Girl',
                    'description': '24/7 lo-fi study music',
                    'url': 'https://www.youtube.com/c/LofiGirl',
                    'resource_type': 'website',
                    'activity_type': 'study',
                    'icon': '🌙',
                    'is_free': True
                }
            ]
        
        elif category.name == '🧠 Health & Fitness':
            resources_data = [
                {
                    'name': 'Nike Training Club',
                    'description': 'Free workout routines',
                    'url': 'https://www.nike.com/ntc-app',
                    'resource_type': 'app',
                    'activity_type': 'workout',
                    'icon': '👟',
                    'is_free': True
                },
                {
                    'name': 'MyFitnessPal',
                    'description': 'Calorie and nutrition tracking',
                    'url': 'https://www.myfitnesspal.com/',
                    'resource_type': 'app',
                    'activity_type': 'meal',
                    'icon': '🍎',
                    'is_free': True
                },
                {
                    'name': 'Headspace',
                    'description': 'Meditation and mindfulness',
                    'url': 'https://www.headspace.com/',
                    'resource_type': 'app',
                    'activity_type': 'break',
                    'icon': '🧘',
                    'is_free': False
                },
                {
                    'name': 'Calm',
                    'description': 'Meditation and sleep app',
                    'url': 'https://www.calm.com/',
                    'resource_type': 'app',
                    'activity_type': 'break',
                    'icon': '🌊',
                    'is_free': False
                },
                {
                    'name': 'Strava',
                    'description': 'Fitness and running tracker',
                    'url': 'https://www.strava.com/',
                    'resource_type': 'app',
                    'activity_type': 'workout',
                    'icon': '🏃',
                    'is_free': True
                }
            ]
        
        elif category.name == '📱 Social & Communication':
            resources_data = [
                {
                    'name': 'WhatsApp',
                    'description': 'Messaging and calls',
                    'url': 'https://web.whatsapp.com/',
                    'resource_type': 'app',
                    'activity_type': 'relationship',
                    'icon': '💬',
                    'is_free': True
                },
                {
                    'name': 'Discord',
                    'description': 'Community and group chats',
                    'url': 'https://discord.com/',
                    'resource_type': 'app',
                    'activity_type': 'relationship',
                    'icon': '🎮',
                    'is_free': True
                },
                {
                    'name': 'Zoom',
                    'description': 'Video conferencing',
                    'url': 'https://zoom.us/',
                    'resource_type': 'app',
                    'activity_type': 'meeting',
                    'icon': '📹',
                    'is_free': True
                },
                {
                    'name': 'Google Meet',
                    'description': 'Video meetings',
                    'url': 'https://meet.google.com/',
                    'resource_type': 'app',
                    'activity_type': 'meeting',
                    'icon': '🎥',
                    'is_free': True
                },
                {
                    'name': 'Slack',
                    'description': 'Team communication',
                    'url': 'https://slack.com/',
                    'resource_type': 'app',
                    'activity_type': 'meeting',
                    'icon': '💼',
                    'is_free': True
                }
            ]
        
        elif category.name == '🎥 Video & Media':
            resources_data = [
                {
                    'name': 'YouTube',
                    'description': 'Video streaming platform',
                    'url': 'https://www.youtube.com/',
                    'resource_type': 'website',
                    'activity_type': 'break',
                    'icon': '📺',
                    'is_free': True
                },
                {
                    'name': 'Netflix',
                    'description': 'Movie and TV streaming',
                    'url': 'https://www.netflix.com/',
                    'resource_type': 'website',
                    'activity_type': 'break',
                    'icon': '🎬',
                    'is_free': False
                },
                {
                    'name': 'Disney+',
                    'description': 'Disney, Marvel, Star Wars content',
                    'url': 'https://www.disneyplus.com/',
                    'resource_type': 'website',
                    'activity_type': 'break',
                    'icon': '🏰',
                    'is_free': False
                },
                {
                    'name': 'Twitch',
                    'description': 'Live streaming platform',
                    'url': 'https://www.twitch.tv/',
                    'resource_type': 'website',
                    'activity_type': 'break',
                    'icon': '🟣',
                    'is_free': True
                },
                {
                    'name': 'TikTok',
                    'description': 'Short form video platform',
                    'url': 'https://www.tiktok.com/',
                    'resource_type': 'app',
                    'activity_type': 'break',
                    'icon': '🎵',
                    'is_free': True
                }
            ]
        
        elif category.name == '📰 News & Information':
            resources_data = [
                {
                    'name': 'BBC News',
                    'description': 'International news coverage',
                    'url': 'https://www.bbc.com/news',
                    'resource_type': 'website',
                    'activity_type': 'break',
                    'icon': '🇬🇧',
                    'is_free': True
                },
                {
                    'name': 'CNN',
                    'description': 'News and current events',
                    'url': 'https://edition.cnn.com/',
                    'resource_type': 'website',
                    'activity_type': 'break',
                    'icon': '📰',
                    'is_free': True
                },
                {
                    'name': 'Al Jazeera',
                    'description': 'Global news network',
                    'url': 'https://www.aljazeera.com/',
                    'resource_type': 'website',
                    'activity_type': 'break',
                    'icon': '🌍',
                    'is_free': True
                },
                {
                    'name': 'Reuters',
                    'description': 'International news agency',
                    'url': 'https://www.reuters.com/',
                    'resource_type': 'website',
                    'activity_type': 'break',
                    'icon': '📊',
                    'is_free': True
                },
                {
                    'name': 'TechCrunch',
                    'description': 'Technology news',
                    'url': 'https://techcrunch.com/',
                    'resource_type': 'website',
                    'activity_type': 'break',
                    'icon': '💻',
                    'is_free': True
                }
            ]
        
        elif category.name == '🛒 Shopping & Services':
            resources_data = [
                {
                    'name': 'Amazon',
                    'description': 'Online shopping marketplace',
                    'url': 'https://www.amazon.com/',
                    'resource_type': 'website',
                    'activity_type': 'break',
                    'icon': '📦',
                    'is_free': True
                },
                {
                    'name': 'Jumia',
                    'description': 'African online marketplace',
                    'url': 'https://www.jumia.co.ke/',
                    'resource_type': 'website',
                    'activity_type': 'break',
                    'icon': '🛍️',
                    'is_free': True
                },
                {
                    'name': 'eBay',
                    'description': 'Online auctions and shopping',
                    'url': 'https://www.ebay.com/',
                    'resource_type': 'website',
                    'activity_type': 'break',
                    'icon': '💰',
                    'is_free': True
                },
                {
                    'name': 'AliExpress',
                    'description': 'International online retail',
                    'url': 'https://www.aliexpress.com/',
                    'resource_type': 'website',
                    'activity_type': 'break',
                    'icon': '🚢',
                    'is_free': True
                },
                {
                    'name': 'Uber Eats',
                    'description': 'Food delivery service',
                    'url': 'https://www.ubereats.com/',
                    'resource_type': 'app',
                    'activity_type': 'meal',
                    'icon': '🍔',
                    'is_free': True
                }
            ]
        
        elif category.name == '💼 JKUAT Specific':
            resources_data = [
                {
                    'name': 'JKUAT eLearning Portal',
                    'description': 'Official JKUAT online learning platform',
                    'url': 'https://elearning.jkuat.ac.ke/',
                    'resource_type': 'website',
                    'activity_type': 'lecture',
                    'icon': '🏫',
                    'is_free': True
                },
                {
                    'name': 'JKUAT Library Portal', 
                    'description': 'Digital library resources and databases',
                    'url': 'https://library.jkuat.ac.ke/',
                    'resource_type': 'website',
                    'activity_type': 'study',
                    'icon': '📚',
                    'is_free': True
                },
                {
                    'name': 'JKUAT Student Portal',
                    'description': 'Student information and registration system',
                    'url': 'https://student.jkuat.ac.ke/',
                    'resource_type': 'website',
                    'activity_type': 'academic',
                    'icon': '🎓',
                    'is_free': True
                },
                {
                    'name': 'JKUAT Past Papers',
                    'description': 'Repository of previous exam papers',
                    'url': 'https://repository.jkuat.ac.ke/',
                    'resource_type': 'website',
                    'activity_type': 'study',
                    'icon': '📝',
                    'is_free': True
                },
                {
                    'name': 'JKUAT Website',
                    'description': 'Official university website',
                    'url': 'https://www.jkuat.ac.ke/',
                    'resource_type': 'website',
                    'activity_type': 'academic',
                    'icon': '🌐',
                    'is_free': True
                }
            ]
        
        # Create resources
        for resource_data in resources_data:
            ActivityResource.objects.get_or_create(
                category=category,
                name=resource_data['name'],
                defaults=resource_data
            )

class ActivityResource(models.Model):
    RESOURCE_TYPES = [
        ('website', '🌐 Website'),
        ('app', '📱 Mobile App'),
        ('course', '📚 Course'),
        ('tool', '🛠️ Tool'),
        ('video', '🎥 Video'),
        ('book', '📖 Book'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(ResourceCategory, on_delete=models.CASCADE, related_name='resources')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    url = models.URLField()
    resource_type = models.CharField(max_length=15, choices=RESOURCE_TYPES)
    activity_type = models.CharField(max_length=20, choices=Schedule.ACTIVITY_TYPES, blank=True)
    icon = models.CharField(max_length=10, default='🔗')
    is_free = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'activity_resources'
        ordering = ['category', 'name']
    
    def __str__(self):
        return self.name

class UserResourcePreference(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resource_preferences')
    resource = models.ForeignKey(ActivityResource, on_delete=models.CASCADE)
    is_favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_resource_preferences'
        unique_together = ['user', 'resource']
    
    def __str__(self):
        return f"{self.user.username} - {self.resource.name}"

class DailyFocus(models.Model):
    """Daily motivational focus quotes"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quote = models.TextField()
    author = models.CharField(max_length=100, blank=True)
    category = models.CharField(max_length=50, choices=SmartActivity.CATEGORY_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'daily_focus'
        verbose_name_plural = 'Daily Focus Quotes'
    
    def __str__(self):
        return f"{self.category} - {self.quote[:50]}..."