from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Profile, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ("username", "email", "is_staff", "is_active", "is_verified")
    list_filter = ("is_staff", "is_active", "is_verified", "user_type", "department")
    search_fields = ("username", "email", "first_name", "last_name", "student_id")
    ordering = ("date_joined",)

    fieldsets = (
        (None, {"fields": ("username", "email", "password")}),
        (
            "Personal info",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "student_id",
                    "user_type",
                    "department",
                    "series",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "is_verified",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2"),
            },
        ),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "birth_date", "reputation_score")
    search_fields = ("user__username", "user__first_name", "user__last_name", "phone")
    readonly_fields = ("created_at", "updated_at")
    list_filter = ("reputation_score", "show_email", "show_phone")
