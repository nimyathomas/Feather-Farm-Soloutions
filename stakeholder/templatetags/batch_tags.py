from django import template

register = template.Library()

@register.filter
def subtract(value, arg):
    return value - arg

@register.filter
def abs(value):
    """Return the absolute value"""
    return abs(value)

@register.filter
def multiply(value, arg):
    """Multiply the value by the argument"""
    return value * arg 