from django import template

register = template.Library()


@register.filter
def split_skills(value):
    if not value:
        return []
    return [item.strip() for item in str(value).replace(";", ",").replace("|", ",").split(",") if item.strip()]
