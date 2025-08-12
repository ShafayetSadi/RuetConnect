from django.contrib import admin

from .models import Thread

# Register your models here.
@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ("title", "organization", "thread_type", "is_pinned", "created_at")
    search_fields = ("title", "description", "organization__name")
    list_filter = ("thread_type", "is_pinned", "is_locked")
