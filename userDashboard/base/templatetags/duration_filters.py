from django import template

register = template.Library()

@register.filter
def format_duration(duration):
    """Format a timedelta object as hours and minutes"""
    if not duration:
        return "-"
    
    total_seconds = duration.total_seconds()
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    
    if duration.days > 0:
        return f"{duration.days}d {hours}h {minutes}m"
    else:
        return f"{hours}h {minutes}m" 