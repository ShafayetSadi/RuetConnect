from django.contrib import admin
from .models import Thread, Subscribed

# Register your models here.
admin.site.register(Thread)
admin.site.register(Subscribed)
