from django.contrib import admin

from .models import Comment

# Register your models here.


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("author", "post", "content", "date_posted", "date_updated")
    list_filter = ("author", "date_posted")
    search_fields = ("author__username", "post__title")
    date_hierarchy = "date_posted"
    ordering = ("date_posted", "date_updated")
