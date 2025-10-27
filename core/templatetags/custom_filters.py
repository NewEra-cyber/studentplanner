from django import template
from datetime import timedelta

register = template.Library()

@register.filter
def add_days(date, days):
    """Add days to a date"""
    if date:
        return date + timedelta(days=int(days))
    return date

@register.filter
def get_range(value):
    """Create a range for template loops"""
    return range(value)

@register.filter
def get_item(dictionary, key):
    """Get dictionary item by key in templates"""
    return dictionary.get(key)