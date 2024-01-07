from django.db import models
from django.urls import reverse

from threads.models import Thread


# Create your models here.


class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()

    author = models.ForeignKey('users.User', related_name='posts', on_delete=models.CASCADE)
    thread = models.ForeignKey('threads.Thread', related_name='posts', on_delete=models.CASCADE)
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    date_posted = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.thread:
            self.thread = Thread.objects.get_or_create(name='ruet')
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
