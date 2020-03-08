from django import template

register = template.Library()

@register.filter()
def spacify(value):
    return value.replace(' ','-')