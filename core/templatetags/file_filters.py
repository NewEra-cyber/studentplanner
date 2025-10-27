from django import template
import os

register = template.Library()

@register.filter
def endswith(value, arg):
    """Custom filter to check if string ends with given argument"""
    if isinstance(value, str) and isinstance(arg, str):
        return value.endswith(arg)
    return False

@register.filter
def filesizeformat(value):
    """
    Format the value like a 'human-readable' file size (i.e. 13 KB, 4.1 MB, 102 bytes, etc.).
    """
    try:
        bytes = float(value)
    except (TypeError, ValueError, UnicodeDecodeError):
        return "0 bytes"
    
    if bytes < 1024:
        return "%d bytes" % bytes
    if bytes < 1024 * 1024:
        return "%.1f KB" % (bytes / 1024)
    if bytes < 1024 * 1024 * 1024:
        return "%.1f MB" % (bytes / (1024 * 1024))
    return "%.1f GB" % (bytes / (1024 * 1024 * 1024))