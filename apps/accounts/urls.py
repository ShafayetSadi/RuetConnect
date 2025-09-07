from django.urls import path

from .views import (
    user_detail,
    user_update,
    user_posts,
    user_comments,
    user_upvoted,
    user_downvoted,
)

urlpatterns = [
    path("user/update/", user_update, name="user-update"),
    path("<str:username>/", user_detail, name="user-detail"),
    path("<str:username>/posts/", user_posts, name="user-posts"),
    path("<str:username>/comments/", user_comments, name="user-comments"),
    path("<str:username>/upvoted/", user_upvoted, name="user-upvoted"),
    path("<str:username>/downvoted/", user_downvoted, name="user-downvoted"),
]
