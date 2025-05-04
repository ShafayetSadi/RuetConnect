from django.db import models

# Create your models here.


class Comment(models.Model):
    content = models.TextField()

    author = models.ForeignKey(
        "accounts.User", related_name="comments", on_delete=models.CASCADE
    )
    post = models.ForeignKey(
        "posts.Post", related_name="comments", on_delete=models.CASCADE
    )

    date_posted = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.author.username + " -> " + self.post.title
