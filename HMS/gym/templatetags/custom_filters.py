from django import template

register = template.Library()

@register.filter
def ifnotcancelled(memberships):
    return sum(1 for membership in memberships if not membership.is_cancelled)
