# home/templatetags/custom_filters.py

from django import template
from django.contrib.humanize.templatetags.humanize import intcomma

register = template.Library()

@register.filter
def format_price(value):
    """Format integer as a price with dots as thousands separators."""
    # Use intcomma to add commas and then replace commas with dots
    formatted_value = intcomma(value)
    return formatted_value.replace(",", ".")

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)