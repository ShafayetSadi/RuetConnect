from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile

# Register your models here.


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_email', 'name', 'image')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'

    def name(self, obj):
        return obj.user.first_name + ' ' + obj.user.last_name
    name.short_description = 'Name'


admin.site.register(User, UserAdmin)
admin.site.register(Profile, ProfileAdmin)
