from django.db import models
from apps.users.models import User


class Thread(models.Model):
    name = models.SlugField(max_length=30, unique=True)
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User, related_name='threads', on_delete=models.CASCADE)
    subscribers = models.ManyToManyField(User, through='Subscribed', related_name='subscribed_threads', blank=True)
    image = models.ImageField(default='thread.jpg', upload_to='thread_pics', blank=True)
    banner = models.ImageField(default='banner.jpg', upload_to='thread_banners', blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.title:
            self.title = self.name
        super().save(*args, **kwargs)
        from django.core.cache import cache
        cache.delete('threads')
        cache.delete('thread_{}'.format(self.name))


class Subscribed(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
    subscribed_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'thread')

    def __str__(self):
        return '{} subscribed to {}'.format(self.user, self.thread)
