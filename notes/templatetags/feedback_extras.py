from django import template

register = template.Library()

@register.filter
def average_rating(feedbacks):
    if not feedbacks:
        return "No ratings"
    total = sum(fb.rating for fb in feedbacks)
    count = len(feedbacks)
    return round(total / count, 2)
