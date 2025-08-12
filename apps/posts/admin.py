from django.contrib import admin

from .models import Post, PostMedia, PostLink


class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "post_type", "is_pinned", "created_at")
    list_filter = ("post_type", "is_pinned", "is_locked", "is_approved")
    search_fields = ("title", "content", "author__username")
    prepopulated_fields = {"slug": ("title",)}


admin.site.register(Post, PostAdmin)
admin.site.register(PostMedia)
admin.site.register(PostLink)
