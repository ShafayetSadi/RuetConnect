import uuid

from django.db import models
from django.urls import reverse
from django.utils.text import slugify

# Create your models here.


class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()

    author = models.ForeignKey(
        "users.User", related_name="posts", on_delete=models.CASCADE
    )
    thread = models.ForeignKey(
        "threads.Thread", related_name="posts", on_delete=models.CASCADE
    )
    slug = models.SlugField(max_length=255, unique=True)

    date_posted = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("post-detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if self._state.adding:
            if not self.slug:
                self.slug = slugify(self.title)
            while Post.objects.filter(slug=self.slug).exists():
                unique_id = str(uuid.uuid4())[:5]
                self.slug = f"{self.slug}-{unique_id}"
        super().save(*args, **kwargs)
