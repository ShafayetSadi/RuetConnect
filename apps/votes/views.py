from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from apps.comments.models import Comment
from apps.posts.models import Post

from .models import SavedPost, Vote


def _get_model_and_ct(model_name: str):
    model_map = {
        "post": Post,
        "comment": Comment,
    }
    Model = model_map.get(model_name)
    if not Model:
        raise Http404("Unsupported model for voting")
    return Model, ContentType.objects.get_for_model(Model)


@login_required
@require_POST
@transaction.atomic
def vote(request):
    model_name = request.POST.get("model")
    object_id = request.POST.get("object_id")
    action = request.POST.get("action")  # 'up', 'down', 'clear'

    if not (model_name and object_id and action):
        return JsonResponse({"error": "Invalid parameters"}, status=400)

    Model, ct = _get_model_and_ct(model_name)
    try:
        pk = int(object_id)
    except (TypeError, ValueError):
        return JsonResponse({"error": "Invalid object id"}, status=400)

    target = get_object_or_404(Model, pk=pk)

    previous = Vote.objects.filter(user=request.user, content_type=ct, object_id=pk).first()

    def dec_up():
        if hasattr(target, "upvotes") and target.upvotes > 0:
            target.upvotes -= 1

    def dec_down():
        if hasattr(target, "downvotes") and target.downvotes > 0:
            target.downvotes -= 1

    def inc_up():
        if hasattr(target, "upvotes"):
            target.upvotes += 1

    def inc_down():
        if hasattr(target, "downvotes"):
            target.downvotes += 1

    if action == "clear":
        if previous:
            if previous.vote_type == 1:
                dec_up()
            elif previous.vote_type == -1:
                dec_down()
            previous.delete()
    elif action in {"up", "down"}:
        new_value = 1 if action == "up" else -1
        if not previous:
            Vote.objects.create(
                user=request.user, content_type=ct, object_id=pk, vote_type=new_value
            )
            if new_value == 1:
                inc_up()
            else:
                inc_down()
        else:
            if previous.vote_type == new_value:
                # toggle off
                if new_value == 1:
                    dec_up()
                else:
                    dec_down()
                previous.delete()
            else:
                # switch vote
                if new_value == 1:
                    inc_up()
                    dec_down()
                else:
                    inc_down()
                    dec_up()
                previous.vote_type = new_value
                previous.save(update_fields=["vote_type"])
    else:
        return JsonResponse({"error": "Unsupported action"}, status=400)

    target.save(update_fields=[
        f for f in ["upvotes", "downvotes", "updated_at"] if hasattr(target, f)
    ])

    payload = {
        "upvotes": getattr(target, "upvotes", None),
        "downvotes": getattr(target, "downvotes", None),
        "score": getattr(target, "upvotes", 0) - getattr(target, "downvotes", 0),
        "object_id": pk,
        "model": model_name,
    }
    return JsonResponse(payload)


@login_required
@require_POST
def toggle_save_post(request, slug: str):
    post = get_object_or_404(Post, slug=slug)
    saved, created = SavedPost.objects.get_or_create(user=request.user, post=post)
    if not created:
        saved.delete()
        is_saved = False
    else:
        is_saved = True
    return JsonResponse({"saved": is_saved, "slug": slug})
