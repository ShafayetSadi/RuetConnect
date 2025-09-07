from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from shared.models import BaseModel


class PostManager(models.Manager):
    """Custom manager for Post model with visibility filtering"""

    def visible_to_user(self, user):
        """
        Return posts that are visible to the given user
        """
        if user.is_authenticated:
            # Get user's organization memberships
            from apps.campus.models import OrganizationMembership

            user_orgs = OrganizationMembership.objects.filter(
                user=user, status="active"
            ).values_list("organization_id", flat=True)

            # Get user's thread memberships
            from apps.threads.models import ThreadMembership

            user_threads = ThreadMembership.objects.filter(
                user=user, status="active"
            ).values_list("thread_id", flat=True)

            # Filter out deleted posts and ensure thread/organization relationships exist
            return self.filter(
                models.Q(visibility="public")
                | models.Q(
                    visibility="organization",
                    thread__organization_id__in=user_orgs,
                    thread__organization__isnull=False,
                )
                | models.Q(visibility="thread", thread_id__in=user_threads)
            ).exclude(is_deleted=True)
        else:
            # Anonymous users can only see public posts
            return self.filter(visibility="public").exclude(is_deleted=True)

    def visible_to_organization(self, organization):
        """
        Return posts from threads that belong to the organization
        """
        return self.filter(
            thread__organization=organization
        ).exclude(is_deleted=True)

    def visible_to_thread(self, thread):
        """
        Return posts visible to thread members
        """
        return self.filter(
            models.Q(visibility="public")
            | models.Q(
                visibility="organization", thread__organization=thread.organization
            )
            | models.Q(visibility="thread", thread=thread)
        )


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

    VISIBILITY_CHOICES = [
        ("thread", "Thread Members Only"),
        ("organization", "Organization Members"),
        ("public", "Public"),
    ]

    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=350, unique=True, blank=True)
    content = models.TextField()
    post_type = models.CharField(max_length=10, choices=POST_TYPES, default="text")
    visibility = models.CharField(
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default="thread",
        help_text="Who can see this post?",
    )
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

    # Custom manager
    objects = PostManager()

    class Meta:
        db_table = "posts"
        ordering = ["-is_pinned", "-updated_at"]
        indexes = [
            models.Index(fields=["thread", "-updated_at"]),
            models.Index(fields=["author", "-updated_at"]),
            models.Index(fields=["-is_pinned", "-updated_at"]),
            models.Index(fields=["post_type"]),
            models.Index(fields=["visibility"]),
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
            max_attempts = 100
            while (
                Post.objects.filter(slug=slug_candidate).exists()
                and counter <= max_attempts
            ):
                slug_candidate = f"{base_slug}-{counter}"
                counter += 1
            if counter > max_attempts:
                # Fallback to UUID if we hit the limit
                import uuid

                slug_candidate = f"{base_slug}-{uuid.uuid4().hex[:8]}"
            self.slug = slug_candidate
        else:
            # Ensure slug remains unique on updates
            if Post.objects.exclude(pk=self.pk).filter(slug=slug_candidate).exists():
                counter = 1
                slug_candidate = base_slug
                max_attempts = 100
                while (
                    Post.objects.exclude(pk=self.pk)
                    .filter(slug=slug_candidate)
                    .exists()
                    and counter <= max_attempts
                ):
                    slug_candidate = f"{base_slug}-{counter}"
                    counter += 1
                if counter > max_attempts:
                    # Fallback to UUID if we hit the limit
                    import uuid

                    slug_candidate = f"{base_slug}-{uuid.uuid4().hex[:8]}"
                self.slug = slug_candidate

        super().save(*args, **kwargs)

    @property
    def score(self):
        return self.upvotes - self.downvotes

    def can_user_view(self, user):
        """
        Check if a user can view this post based on visibility settings
        """
        # Check if post is deleted
        if self.is_deleted:
            return False

        # Public posts are visible to everyone
        if self.visibility == "public":
            return True

        # For non-public posts, user must be authenticated
        if not user.is_authenticated:
            return False

        # Check if thread and organization exist
        if not hasattr(self, "thread") or not self.thread:
            return False

        if self.visibility == "organization" and not self.thread.organization:
            return False

        # Organization visibility - user must be active member of the organization
        if self.visibility == "organization":
            from apps.campus.models import OrganizationMembership

            return OrganizationMembership.objects.filter(
                organization=self.thread.organization, user=user, status="active"
            ).exists()

        # Thread visibility - user must be active member of the thread
        if self.visibility == "thread":
            from apps.threads.models import ThreadMembership

            return ThreadMembership.objects.filter(
                thread=self.thread, user=user, status="active"
            ).exists()

        return False

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
