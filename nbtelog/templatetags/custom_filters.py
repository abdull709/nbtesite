from django import template

register = template.Library()

@register.filter
def endswith(value, arg):
    """Check if a string ends with the given argument"""
    try:
        return value.endswith(arg)
    except (AttributeError, TypeError):
        return False

@register.filter
def split(value, arg):
    """Split a string by the given argument"""
    try:
        return value.split(arg)
    except (AttributeError, TypeError):
        return [value] 