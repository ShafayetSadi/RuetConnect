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
            while Thread.objects.filter(slug=slug_candidate).exists():
                slug_candidate = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug_candidate
        else:
            if Thread.objects.exclude(pk=self.pk).filter(slug=slug_candidate).exists():
                counter = 1
                slug_candidate = base_slug
                while (
                    Thread.objects.exclude(pk=self.pk).filter(slug=slug_candidate).exists()
                ):
                    slug_candidate = f"{base_slug}-{counter}"
                    counter += 1
                self.slug = slug_candidate

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("thread-detail", kwargs={"thread_name": self.slug})

    def __str__(self):
        return self.title
