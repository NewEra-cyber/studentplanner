from django.core.management.base import BaseCommand
from core.models import ActivityResource, ResourceCategory

class Command(BaseCommand):
    help = 'Add missing resources'
    
    def handle(self, *args, **options):
        # Get or create Web Development category
        web_dev_category, created = ResourceCategory.objects.get_or_create(
            name='Web Development',
            defaults={
                'category_type': 'programming',
                'icon': '🌐',
                'color': '#2563EB'
            }
        )
        
        # Add W3Schools if missing
        w3schools, created = ActivityResource.objects.get_or_create(
            name='W3Schools',
            url='https://www.w3schools.com',
            defaults={
                'category': web_dev_category,
                'activity_type': 'study',
                'resource_type': 'website',
                'icon': '🏫',
                'is_free': True,
                'is_recommended': True,
                'description': 'Beginner-friendly web development tutorials'
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('✅ Added W3Schools to Web Development'))
        else:
            self.stdout.write(self.style.SUCCESS('✅ W3Schools already exists'))
        
        # Count resources by category
        for category in ResourceCategory.objects.all():
            count = ActivityResource.objects.filter(category=category).count()
            self.stdout.write(f"📁 {category.name}: {count} resources")