from django.db import models
from shared.models import BaseModel


class Comment(BaseModel):
    """Nested comments system"""

    post = models.ForeignKey(
        "posts.Post", on_delete=models.CASCADE, related_name="comments"
    )
    author = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="comments"
    )
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies"
    )
    content = models.TextField()

    # Engagement
    upvotes = models.PositiveIntegerField(default=0)
    downvotes = models.PositiveIntegerField(default=0)

    # Status
    is_deleted = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)

    # Hierarchy
    level = models.PositiveIntegerField(default=0)  # For nested depth
    path = models.CharField(max_length=500, blank=True)  # Materialized path

    class Meta:
        db_table = "comments"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["post", "-created_at"]),
            models.Index(fields=["parent"]),
            models.Index(fields=["path"]),
        ]

    def save(self, *args, **kwargs):
        if self.parent:
            self.level = self.parent.level + 1
            # Limit path length to prevent database field overflow
            new_path = f"{self.parent.path}/{self.parent.id}"
            if len(new_path) > 500:  # Max length of path field
                # Truncate path if it gets too long
                self.path = new_path[-500:]
            else:
                self.path = new_path
        else:
            self.level = 0
            self.path = ""
        super().save(*args, **kwargs)

    @property
    def score(self):
        return self.upvotes - self.downvotes
