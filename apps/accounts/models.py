from django.contrib.auth.models import AbstractUser
from django.db import models
from PIL import Image

from shared.models import BaseModel


class User(AbstractUser):
    """Extended user model for RUET students/faculty"""

    USER_TYPES = [
        ("student", "Student"),
        ("faculty", "Faculty"),
        ("staff", "Staff"),
        ("alumni", "Alumni"),
    ]

    DEPARTMENTS = [
        ("cse", "Computer Science & Engineering"),
        ("eee", "Electrical & Electronic Engineering"),
        ("me", "Mechanical Engineering"),
        ("ce", "Civil Engineering"),
        ("ipe", "Industrial & Production Engineering"),
        ("che", "Chemical Engineering"),
        ("mte", "Materials & Metallurgical Engineering"),
        ("arch", "Architecture"),
        ("urp", "Urban & Regional Planning"),
        ("math", "Mathematics"),
        ("phy", "Physics"),
        ("chem", "Chemistry"),
        ("hum", "Humanities"),
    ]

    id = models.BigAutoField(primary_key=True)

    student_id = models.CharField(
        max_length=7,
        unique=True,
        null=True,
        blank=True,
        help_text="Student ID is required for students",
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default="student")
    department = models.CharField(
        max_length=10,
        choices=DEPARTMENTS,
        blank=True,
        help_text="Academic department of the user",
    )
    series = models.CharField(
        max_length=4,
        null=True,
        blank=True,
        help_text="Admission year (e.g., 2019)",
    )
    is_verified = models.BooleanField(default=False, help_text="Verified RUET member")
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "users"
        indexes = [
            models.Index(fields=["department", "series"]),
            models.Index(fields=["user_type"]),
            models.Index(fields=["student_id"]),
            models.Index(fields=["is_verified"]),
        ]

    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name or self.username

    def get_display_name(self):
        """Return display name for UI"""
        if self.first_name and self.last_name:
            return self.get_full_name()
        return self.username

    @property
    def is_student(self):
        return self.user_type == "student"

    @property
    def is_faculty(self):
        return self.user_type == "faculty"

    def __str__(self):
        if self.user_type == "student":
            return f"{self.student_id} - {self.first_name} {self.last_name}"
        elif self.user_type == "faculty":
            return f"{self.first_name} {self.last_name} - {self.department}"
        else:
            return f"{self.first_name} {self.last_name}"


class Profile(BaseModel):
    """Profile model for User"""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile", primary_key=True
    )
    birth_date = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(
        upload_to="avatars/", null=True, blank=True, help_text="Profile picture"
    )
    social_links = models.JSONField(
        default=dict,
        blank=True,
        help_text="Social media links as JSON: {'facebook': 'url', 'linkedin': 'url'}",
    )
    interests = models.JSONField(
        default=list,
        blank=True,
        help_text="List of interests: ['programming', 'robotics']",
    )
    skills = models.JSONField(default=list, blank=True, help_text="List of skills")
    reputation_score = models.IntegerField(default=0)

    # Privacy settings
    show_email = models.BooleanField(default=False)
    show_phone = models.BooleanField(default=False)

    class Meta:
        db_table = "user_profiles"
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["birth_date"]),
            models.Index(fields=["reputation_score"]),
        ]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.avatar:
            try:
                img = Image.open(self.avatar.path)
                if img.height > 400 or img.width > 400:
                    output_size = (400, 400)
                    img.thumbnail(output_size)
                    img.save(self.avatar.path)
            except Exception:
                pass

    def __str__(self):
        return f"{self.user.get_display_name()}'s Profile"
