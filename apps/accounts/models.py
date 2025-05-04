from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models

from shared.models import BaseModel


class User(AbstractUser):
    email = models.EmailField(unique=True, max_length=255)
    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[
            UnicodeUsernameValidator(),
            MinLengthValidator(6),
            MaxLengthValidator(30),
        ],
    )
    is_email_verified = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=20, blank=True)
    is_phone_verified = models.BooleanField(default=False)

    REQUIRED_FIELDS = ["email"]
    objects = UserManager()

    def __str__(self):
        return self.username


class Profile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    image = models.ImageField(default="profile.jpg", upload_to="profile_pics")
    social_links = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} Profile"
