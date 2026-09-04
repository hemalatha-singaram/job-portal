from django import template

from skillgap.services import LEARNING_PATHS

register = template.Library()


@register.filter
def split_skills(value):
    if not value:
        return []
    return [item.strip() for item in str(value).replace(";", ",").replace("|", ",").split(",") if item.strip()]


@register.filter
def learning_resource(skill):
    """Return a learning resource for a missing skill."""
    skill_text = str(skill or "").strip()
    for name, resource in LEARNING_PATHS.items():
        if name.lower() == skill_text.lower():
            return resource
    return {
        "description": f"Learn the fundamentals of {skill_text}.",
        "level": "Beginner",
    }
