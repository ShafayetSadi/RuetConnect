from django.urls import path
from . import views

urlpatterns = [
    path('create/<slug:slug>/', views.CommentCreateView.as_view(), name='comment-create'),
]
