from django import template
import os

register = template.Library()

@register.filter
def file_exists(filepath):
    return os.path.exists(filepath) if filepath else False

@register.filter
def multiply(value, arg):
    return float(value) * float(arg)

@register.filter
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class}) 