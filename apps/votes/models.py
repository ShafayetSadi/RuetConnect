from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from shared.models import BaseModel


class Vote(BaseModel):
    """Generic voting system for posts and comments"""

    VOTE_TYPES = [
        (1, "Upvote"),
        (-1, "Downvote"),
    ]

    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    vote_type = models.SmallIntegerField(choices=VOTE_TYPES)

    # Generic foreign key for voting on different models (targets BigAutoField PKs)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        db_table = "votes"
        unique_together = ["user", "content_type", "object_id"]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["user"]),
        ]


class SavedPost(BaseModel):
    """User saved posts"""

    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    post = models.ForeignKey("posts.Post", on_delete=models.CASCADE)

    class Meta:
        db_table = "saved_posts"
        unique_together = ["user", "post"]
