from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from shared.models import BaseModel


class Thread(BaseModel):
    """Discussion threads/categories"""

    THREAD_TYPES = [
        ("general", "General Discussion"),
        ("announcement", "Announcement"),
        ("event", "Event"),
        ("academic", "Academic"),
        ("project", "Project"),
        ("job", "Job/Internship"),
        ("help", "Help & Support"),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    description = models.TextField(blank=True)
    thread_type = models.CharField(
        max_length=20, choices=THREAD_TYPES, default="general"
    )
    organization = models.ForeignKey(
        "campus.Organization", on_delete=models.CASCADE, related_name="threads"
    )
    created_by = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    is_pinned = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    post_count = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "threads"
        ordering = ["-is_pinned", "-updated_at"]
        indexes = [
            models.Index(fields=["organization", "-updated_at"]),
            models.Index(fields=["thread_type"]),
            models.Index(fields=["-is_pinned", "-updated_at"]),
        ]

    def save(self, *args, **kwargs):
        base_slug = slugify(self.title) if not self.slug else self.slug
        if not base_slug:
            base_slug = "thread"
        base_slug = base_slug[:230]

        if not self.slug:
            slug_candidate = base_slug
        else:
            slug_candidate = self.slug

        if self._state.adding:
            counter = 1
            max_attempts = 100
            while (
                Thread.objects.filter(slug=slug_candidate).exists()
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
            if Thread.objects.exclude(pk=self.pk).filter(slug=slug_candidate).exists():
                counter = 1
                slug_candidate = base_slug
                max_attempts = 100
                while (
                    Thread.objects.exclude(pk=self.pk)
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

    def get_absolute_url(self):
        return reverse("thread-detail", kwargs={"thread_name": self.slug})

    def __str__(self):
        return self.title


class ThreadMembership(BaseModel):
    """User membership/role within a specific thread.

    A user must be an active member of the parent Organization to be eligible for
    thread membership.
    """

    ROLES = [
        ("member", "Member"),
        ("moderator", "Moderator"),
        ("admin", "Admin"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("banned", "Banned"),
    ]

    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    thread = models.ForeignKey("threads.Thread", on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLES, default="member")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")

    class Meta:
        db_table = "thread_memberships"
        unique_together = ["user", "thread"]
        indexes = [
            models.Index(fields=["thread", "status", "role"]),
            models.Index(fields=["user", "status", "role"]),
        ]
