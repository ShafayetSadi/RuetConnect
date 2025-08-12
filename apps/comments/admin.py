from django.contrib import admin

from .models import Comment

# Register your models here.


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("author", "post", "content", "created_at", "updated_at")
    list_filter = ("author", "created_at")
    search_fields = ("author__username", "post__title", "content")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
