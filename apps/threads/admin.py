from django.contrib import admin

from .models import Thread, ThreadMembership

@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ("title", "organization", "thread_type", "is_pinned", "created_at")
    search_fields = ("title", "description", "organization__name")
    list_filter = ("thread_type", "is_pinned", "is_locked")


@admin.register(ThreadMembership)
class ThreadMembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "thread", "role", "status", "created_at")
    search_fields = ("user__username", "thread__title")
    list_filter = ("role", "status")
