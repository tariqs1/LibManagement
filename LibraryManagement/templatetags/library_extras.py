from django import template
from django.db.models import Avg

register = template.Library()

@register.filter
def times(number):
    """Returns a range of numbers for star ratings"""
    try:
        return range(int(float(number)))
    except (ValueError, TypeError):
        return range(0)

@register.filter
def subtract(value, arg):
    """Subtracts the arg from the value"""
    try:
        return int(float(value)) - int(float(arg))
    except (ValueError, TypeError):
        return 0

@register.filter
def avg(queryset, attr_name):
    """Returns the average of an attribute on a queryset"""
    if not queryset:
        return 0
    return queryset.aggregate(avg=Avg(attr_name))['avg'] or 0