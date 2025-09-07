from django import template
from django.contrib.contenttypes.models import ContentType
from apps.votes.models import Vote

register = template.Library()


@register.simple_tag(takes_context=True)
def user_vote(context, obj):
    """Return 1, -1 or 0 for the current user's vote on obj."""
    request = context.get("request")
    if not request or not hasattr(request, "user") or not request.user.is_authenticated:
        return 0
    ct = ContentType.objects.get_for_model(obj.__class__)
    v = Vote.objects.filter(
        user=request.user, content_type=ct, object_id=obj.pk
    ).first()
    return v.vote_type if v else 0
