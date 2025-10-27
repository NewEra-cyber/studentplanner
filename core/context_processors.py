from django.conf import settings

def theme_context(request):
    """Add theme and debug context to all templates"""
    return {
        'DEBUG': settings.DEBUG,
        'THEME_VERSION': '2.0.0',
        'APP_NAME': 'PlannerDeep AI',
    }