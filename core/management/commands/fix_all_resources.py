from django.core.management.base import BaseCommand
from core.models import ActivityResource, ResourceCategory
from datetime import time

class Command(BaseCommand):
    help = 'Create ALL missing resources properly'
    
    def handle(self, *args, **options):
        self.stdout.write("🚀 Creating ALL resources...")
        
        # Delete all existing resources and categories to start fresh
        ActivityResource.objects.all().delete()
        ResourceCategory.objects.all().delete()
        
        # Create all categories
        categories_data = [
            {'name': 'Web Development', 'type': 'programming', 'icon': '🌐', 'color': '#2563EB'},
            {'name': 'Database Systems', 'type': 'programming', 'icon': '🗄️', 'color': '#8B5CF6'},
            {'name': 'Software Engineering', 'type': 'programming', 'icon': '⚙️', 'color': '#6B7280'},
            {'name': 'Mobile Computing', 'type': 'programming', 'icon': '📱', 'color': '#059669'},
            {'name': 'OOP Programming', 'type': 'programming', 'icon': '🧩', 'color': '#DC2626'},
            {'name': 'Math & Science', 'type': 'learning', 'icon': '🔬', 'color': '#06B6D4'},
            {'name': 'Learning Platforms', 'type': 'learning', 'icon': '🎓', 'color': '#10B981'},
            {'name': 'Programming & Dev', 'type': 'programming', 'icon': '💻', 'color': '#3B82F6'},
            {'name': 'Productivity Tools', 'type': 'productivity', 'icon': '⚡', 'color': '#F59E0B'},
            {'name': 'Games & Entertainment', 'type': 'entertainment', 'icon': '🎮', 'color': '#8B5CF6'},
            {'name': 'Health & Fitness', 'type': 'health', 'icon': '💪', 'color': '#EF4444'},
            {'name': 'Movies & Streaming', 'type': 'entertainment', 'icon': '🎬', 'color': '#EC4899'},
        ]
        
        categories = {}
        for cat_data in categories_data:
            category, created = ResourceCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'category_type': cat_data['type'],
                    'icon': cat_data['icon'],
                    'color': cat_data['color']
                }
            )
            categories[cat_data['name']] = category
            self.stdout.write(f"✅ Created category: {cat_data['name']}")
        
        # Create ALL resources
        resources_data = [
            # === WEB DEVELOPMENT ===
            {'name': 'MDN Web Docs', 'url': 'https://developer.mozilla.org', 'type': 'website', 'category': 'Web Development', 'activity_type': 'study', 'icon': '📚', 'free': True},
            {'name': 'W3Schools', 'url': 'https://www.w3schools.com', 'type': 'website', 'category': 'Web Development', 'activity_type': 'study', 'icon': '🏫', 'free': True},
            {'name': 'Stack Overflow', 'url': 'https://stackoverflow.com', 'type': 'community', 'category': 'Web Development', 'activity_type': 'project', 'icon': '❓', 'free': True},
            {'name': 'CSS-Tricks', 'url': 'https://css-tricks.com', 'type': 'website', 'category': 'Web Development', 'activity_type': 'skill', 'icon': '🎨', 'free': True},
            {'name': 'Dev.to', 'url': 'https://dev.to', 'type': 'community', 'category': 'Web Development', 'activity_type': 'study', 'icon': '💬', 'free': True},
            
            # === DATABASE SYSTEMS ===
            {'name': 'MySQL Docs', 'url': 'https://dev.mysql.com/doc/', 'type': 'website', 'category': 'Database Systems', 'activity_type': 'study', 'icon': '🐬', 'free': True},
            {'name': 'PostgreSQL Docs', 'url': 'https://www.postgresql.org/docs/', 'type': 'website', 'category': 'Database Systems', 'activity_type': 'study', 'icon': '🐘', 'free': True},
            {'name': 'SQLite Docs', 'url': 'https://www.sqlite.org/docs.html', 'type': 'website', 'category': 'Database Systems', 'activity_type': 'study', 'icon': '💾', 'free': True},
            {'name': 'MongoDB University', 'url': 'https://university.mongodb.com', 'type': 'course', 'category': 'Database Systems', 'activity_type': 'study', 'icon': '🍃', 'free': True},
            
            # === SOFTWARE ENGINEERING ===
            {'name': 'UML Resources', 'url': 'https://www.uml.org', 'type': 'website', 'category': 'Software Engineering', 'activity_type': 'study', 'icon': '📊', 'free': True},
            {'name': 'Agile Manifesto', 'url': 'https://agilemanifesto.org', 'type': 'website', 'category': 'Software Engineering', 'activity_type': 'study', 'icon': '🔄', 'free': True},
            {'name': 'Martin Fowler', 'url': 'https://martinfowler.com', 'type': 'website', 'category': 'Software Engineering', 'activity_type': 'study', 'icon': '👨‍💼', 'free': True},
            {'name': 'GitHub Blog', 'url': 'https://github.blog', 'type': 'website', 'category': 'Software Engineering', 'activity_type': 'study', 'icon': '📰', 'free': True},
            
            # === MOBILE COMPUTING ===
            {'name': 'Android Developer', 'url': 'https://developer.android.com', 'type': 'website', 'category': 'Mobile Computing', 'activity_type': 'skill', 'icon': '🤖', 'free': True},
            {'name': 'iOS Developer', 'url': 'https://developer.apple.com/ios/', 'type': 'website', 'category': 'Mobile Computing', 'activity_type': 'skill', 'icon': '📱', 'free': True},
            {'name': 'React Native', 'url': 'https://reactnative.dev', 'type': 'website', 'category': 'Mobile Computing', 'activity_type': 'skill', 'icon': '⚛️', 'free': True},
            {'name': 'Flutter Docs', 'url': 'https://flutter.dev/docs', 'type': 'website', 'category': 'Mobile Computing', 'activity_type': 'skill', 'icon': '🎯', 'free': True},
            
            # === OOP PROGRAMMING ===
            {'name': 'Java Tutorials', 'url': 'https://docs.oracle.com/javase/tutorial/', 'type': 'website', 'category': 'OOP Programming', 'activity_type': 'study', 'icon': '☕', 'free': True},
            {'name': 'Python Tutorials', 'url': 'https://docs.python.org/3/tutorial/', 'type': 'website', 'category': 'OOP Programming', 'activity_type': 'study', 'icon': '🐍', 'free': True},
            {'name': 'C# Guide', 'url': 'https://learn.microsoft.com/en-us/dotnet/csharp/', 'type': 'website', 'category': 'OOP Programming', 'activity_type': 'study', 'icon': '🔷', 'free': True},
            {'name': 'C++ Reference', 'url': 'https://en.cppreference.com', 'type': 'website', 'category': 'OOP Programming', 'activity_type': 'study', 'icon': '➕', 'free': True},
            
            # === CALCULUS & MATH ===
            {'name': 'Khan Academy', 'url': 'https://www.khanacademy.org/math/calculus-1', 'type': 'course', 'category': 'Math & Science', 'activity_type': 'study', 'icon': '🎓', 'free': True},
            {'name': 'Paul\'s Online Math', 'url': 'https://tutorial.math.lamar.edu', 'type': 'website', 'category': 'Math & Science', 'activity_type': 'study', 'icon': '📐', 'free': True},
            {'name': 'Wolfram Alpha', 'url': 'https://www.wolframalpha.com', 'type': 'tool', 'category': 'Math & Science', 'activity_type': 'study', 'icon': 'α', 'free': True},
            {'name': '3Blue1Brown', 'url': 'https://www.3blue1brown.com', 'type': 'website', 'category': 'Math & Science', 'activity_type': 'study', 'icon': '📊', 'free': True},
            
            # === LEARNING PLATFORMS ===
            {'name': 'Coursera', 'url': 'https://www.coursera.org', 'type': 'course', 'category': 'Learning Platforms', 'activity_type': 'study', 'icon': '🎓', 'free': True},
            {'name': 'Udemy', 'url': 'https://www.udemy.com', 'type': 'course', 'category': 'Learning Platforms', 'activity_type': 'skill', 'icon': '📚', 'free': False},
            {'name': 'freeCodeCamp', 'url': 'https://www.freecodecamp.org', 'type': 'course', 'category': 'Learning Platforms', 'activity_type': 'skill', 'icon': '🆓', 'free': True},
            {'name': 'Codecademy', 'url': 'https://www.codecademy.com', 'type': 'course', 'category': 'Learning Platforms', 'activity_type': 'skill', 'icon': '💻', 'free': False},
            {'name': 'edX', 'url': 'https://www.edx.org', 'type': 'course', 'category': 'Learning Platforms', 'activity_type': 'study', 'icon': '🏫', 'free': True},
            {'name': 'Udacity', 'url': 'https://www.udacity.com', 'type': 'course', 'category': 'Learning Platforms', 'activity_type': 'skill', 'icon': '🚀', 'free': False},
            {'name': 'Codewars', 'url': 'https://www.codewars.com', 'type': 'website', 'category': 'Learning Platforms', 'activity_type': 'skill', 'icon': '⚔️', 'free': True},
            {'name': 'Exercism', 'url': 'https://exercism.org', 'type': 'website', 'category': 'Learning Platforms', 'activity_type': 'skill', 'icon': '💪', 'free': True},
            {'name': 'Codedex', 'url': 'https://www.codedex.io', 'type': 'website', 'category': 'Learning Platforms', 'activity_type': 'skill', 'icon': '💎', 'free': True},
            
            # === PRODUCTIVITY TOOLS ===
            {'name': 'Notion', 'url': 'https://www.notion.so', 'type': 'tool', 'category': 'Productivity Tools', 'activity_type': 'study', 'icon': '📝', 'free': True},
            {'name': 'Trello', 'url': 'https://trello.com', 'type': 'tool', 'category': 'Productivity Tools', 'activity_type': 'project', 'icon': '📋', 'free': True},
            {'name': 'Figma', 'url': 'https://www.figma.com', 'type': 'tool', 'category': 'Productivity Tools', 'activity_type': 'project', 'icon': '🎨', 'free': True},
            {'name': 'Obsidian', 'url': 'https://obsidian.md', 'type': 'tool', 'category': 'Productivity Tools', 'activity_type': 'study', 'icon': '💎', 'free': True},
            {'name': 'Canva', 'url': 'https://www.canva.com', 'type': 'tool', 'category': 'Productivity Tools', 'activity_type': 'project', 'icon': '🖼️', 'free': True},
            {'name': 'Adobe Color', 'url': 'https://color.adobe.com', 'type': 'tool', 'category': 'Productivity Tools', 'activity_type': 'project', 'icon': '🎨', 'free': True},
            
            # === GAMES & ENTERTAINMENT ===
            {'name': 'Chess.com', 'url': 'https://www.chess.com', 'type': 'game', 'category': 'Games & Entertainment', 'activity_type': 'break', 'icon': '♟️', 'free': True},
            {'name': 'Lichess', 'url': 'https://lichess.org', 'type': 'game', 'category': 'Games & Entertainment', 'activity_type': 'break', 'icon': '♚', 'free': True},
            {'name': 'Sudoku.com', 'url': 'https://sudoku.com', 'type': 'game', 'category': 'Games & Entertainment', 'activity_type': 'break', 'icon': '9️⃣', 'free': True},
            {'name': 'CodinGame', 'url': 'https://www.codingame.com', 'type': 'game', 'category': 'Games & Entertainment', 'activity_type': 'skill', 'icon': '🎯', 'free': True},
            {'name': 'NYTimes Games', 'url': 'https://www.nytimes.com/games', 'type': 'game', 'category': 'Games & Entertainment', 'activity_type': 'break', 'icon': '📰', 'free': True},
            
            # === HEALTH & FITNESS ===
            {'name': 'Nike Training Club', 'url': 'https://www.nike.com/ntc-app', 'type': 'app', 'category': 'Health & Fitness', 'activity_type': 'workout', 'icon': '👟', 'free': True},
            {'name': 'MyFitnessPal', 'url': 'https://www.myfitnesspal.com', 'type': 'app', 'category': 'Health & Fitness', 'activity_type': 'meal', 'icon': '🍎', 'free': True},
            {'name': 'Fitness Blender', 'url': 'https://www.fitnessblender.com', 'type': 'website', 'category': 'Health & Fitness', 'activity_type': 'workout', 'icon': '💪', 'free': True},
            {'name': 'StrongLifts 5x5', 'url': 'https://stronglifts.com/5x5/', 'type': 'website', 'category': 'Health & Fitness', 'activity_type': 'workout', 'icon': '🏋️', 'free': True},
            {'name': 'Athlean-X', 'url': 'https://www.youtube.com/c/athleanx', 'type': 'video', 'category': 'Health & Fitness', 'activity_type': 'workout', 'icon': '🔬', 'free': True},
            
            # === MOVIES & STREAMING ===
            {'name': 'Netflix', 'url': 'https://www.netflix.com', 'type': 'app', 'category': 'Movies & Streaming', 'activity_type': 'break', 'icon': '🎬', 'free': False},
            {'name': 'YouTube', 'url': 'https://www.youtube.com', 'type': 'website', 'category': 'Movies & Streaming', 'activity_type': 'break', 'icon': '📺', 'free': True},
            {'name': 'Disney+', 'url': 'https://www.disneyplus.com', 'type': 'app', 'category': 'Movies & Streaming', 'activity_type': 'break', 'icon': '🐭', 'free': False},
            {'name': 'Crunchyroll', 'url': 'https://www.crunchyroll.com', 'type': 'app', 'category': 'Movies & Streaming', 'activity_type': 'break', 'icon': '🇯🇵', 'free': False},
            {'name': 'Spotify', 'url': 'https://www.spotify.com', 'type': 'app', 'category': 'Movies & Streaming', 'activity_type': 'break', 'icon': '🎵', 'free': True},
            {'name': 'SoundCloud', 'url': 'https://soundcloud.com', 'type': 'app', 'category': 'Movies & Streaming', 'activity_type': 'break', 'icon': '☁️', 'free': True},
            {'name': 'JustWatch', 'url': 'https://www.justwatch.com', 'type': 'website', 'category': 'Movies & Streaming', 'activity_type': 'break', 'icon': '🔍', 'free': True},
            
            # === MEAL PLANNING ===
            {'name': 'Tasty', 'url': 'https://tasty.co', 'type': 'app', 'category': 'Health & Fitness', 'activity_type': 'meal', 'icon': '👨‍🍳', 'free': True},
            {'name': 'Budget Bytes', 'url': 'https://www.budgetbytes.com', 'type': 'website', 'category': 'Health & Fitness', 'activity_type': 'meal', 'icon': '💰', 'free': True},
            
            # === CODING PRACTICE ===
            {'name': 'LeetCode', 'url': 'https://leetcode.com', 'type': 'website', 'category': 'Programming & Dev', 'activity_type': 'skill', 'icon': '💡', 'free': True},
            {'name': 'HackerRank', 'url': 'https://hackerrank.com', 'type': 'website', 'category': 'Programming & Dev', 'activity_type': 'skill', 'icon': '⚡', 'free': True},
            {'name': 'GitHub', 'url': 'https://github.com', 'type': 'tool', 'category': 'Programming & Dev', 'activity_type': 'project', 'icon': '🐙', 'free': True},
        ]
        
        created_count = 0
        for res_data in resources_data:
            resource, created = ActivityResource.objects.get_or_create(
                name=res_data['name'],
                url=res_data['url'],
                defaults={
                    'category': categories[res_data['category']],
                    'activity_type': res_data['activity_type'],
                    'resource_type': res_data['type'],
                    'icon': res_data['icon'],
                    'is_free': res_data['free'],
                    'is_recommended': True,
                    'description': f"Great resource for {res_data['activity_type']} activities"
                }
            )
            if created:
                created_count += 1
        
        # Final count
        self.stdout.write(self.style.SUCCESS(f"🎉 Created {created_count} resources!"))
        for category_name, category in categories.items():
            count = ActivityResource.objects.filter(category=category).count()
            self.stdout.write(f"📁 {category_name}: {count} resources")