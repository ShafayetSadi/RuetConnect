from django.contrib import admin

from .models import Subscribed, Thread

# Register your models here.
admin.site.register(Thread)
admin.site.register(Subscribed)
