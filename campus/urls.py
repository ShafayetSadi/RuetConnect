from django.urls import path
from .views import home, about

urlpatterns = [
    path('', home, name='campus-home'),
    path('about/', about, name='campus-about'),
]
