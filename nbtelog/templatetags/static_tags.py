from django import template
from django.conf import settings
import os

register = template.Library()

@register.filter
def static_exists(static_path):
    """Check if a static file exists."""
    # First check in STATIC_ROOT (production)
    if hasattr(settings, 'STATIC_ROOT') and settings.STATIC_ROOT:
        full_path = os.path.join(settings.STATIC_ROOT, static_path)
        if os.path.exists(full_path):
            return True
            
    # Then check in all STATICFILES_DIRS (development)
    for static_dir in settings.STATICFILES_DIRS:
        full_path = os.path.join(static_dir, static_path)
        if os.path.exists(full_path):
            return True
            
    return False