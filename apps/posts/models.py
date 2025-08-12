from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from shared.models import BaseModel


class Post(BaseModel):
    """Forum posts"""

    POST_TYPES = [
        ("text", "Text"),
        ("image", "Image"),
        ("video", "Video"),
        ("link", "Link"),
        ("poll", "Poll"),
        ("event", "Event"),
    ]

    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=350, unique=True, blank=True)
    content = models.TextField()
    post_type = models.CharField(max_length=10, choices=POST_TYPES, default="text")
    thread = models.ForeignKey(
        "threads.Thread", on_delete=models.CASCADE, related_name="posts"
    )
    author = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="posts"
    )

    # Engagement metrics
    upvotes = models.PositiveIntegerField(default=0)
    downvotes = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)

    # Status fields
    is_pinned = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)

    class Meta:
        db_table = "posts"
        ordering = ["-is_pinned", "-updated_at"]
        indexes = [
            models.Index(fields=["thread", "-updated_at"]),
            models.Index(fields=["author", "-updated_at"]),
            models.Index(fields=["-is_pinned", "-updated_at"]),
            models.Index(fields=["post_type"]),
        ]

    def save(self, *args, **kwargs):
        base_slug = slugify(self.title) if not self.slug else self.slug
        if not base_slug:
            base_slug = "post"
        base_slug = base_slug[:240]

        if not self.slug:
            slug_candidate = base_slug
        else:
            slug_candidate = self.slug

        if self._state.adding:
            counter = 1
            while Post.objects.filter(slug=slug_candidate).exists():
                slug_candidate = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug_candidate
        else:
            # Ensure slug remains unique on updates
            if Post.objects.exclude(pk=self.pk).filter(slug=slug_candidate).exists():
                counter = 1
                slug_candidate = base_slug
                while (
                    Post.objects.exclude(pk=self.pk).filter(slug=slug_candidate).exists()
                ):
                    slug_candidate = f"{base_slug}-{counter}"
                    counter += 1
                self.slug = slug_candidate

        super().save(*args, **kwargs)

    @property
    def score(self):
        return self.upvotes - self.downvotes

    def get_absolute_url(self):
        return reverse("post-detail", kwargs={"slug": self.slug})

    def __str__(self):
        return self.title


class PostMedia(BaseModel):
    """Media attachments for posts"""

    MEDIA_TYPES = [
        ("image", "Image"),
        ("video", "Video"),
        ("document", "Document"),
        ("audio", "Audio"),
    ]

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="media")
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES)
    file = models.FileField(upload_to="post_media/")
    caption = models.CharField(max_length=200, blank=True)
    file_size = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        db_table = "post_media"


class PostLink(BaseModel):
    """External links in posts"""

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="links")
    url = models.URLField()
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    thumbnail = models.URLField(blank=True)

    class Meta:
        db_table = "post_links"

