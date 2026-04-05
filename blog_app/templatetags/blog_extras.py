import math
from django import template
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name='reading_time')
def reading_time(content):
    """Return estimated reading time in minutes."""
    text = strip_tags(content)
    word_count = len(text.split())
    minutes = math.ceil(word_count / 200)
    return max(1, minutes)


@register.filter(name='render_html')
def render_html(value):
    """Mark HTML content as safe for rendering."""
    return mark_safe(value)
