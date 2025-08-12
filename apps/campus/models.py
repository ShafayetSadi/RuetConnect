# apps/campus/models.py
from django.db import models
from django.utils.text import slugify
from shared.models import BaseModel


class Organization(BaseModel):
    """Clubs, societies, and organizations"""

    ORG_TYPES = [
        ("club", "Club"),
        ("society", "Society"),
        ("association", "Association"),
        ("committee", "Committee"),
        ("department", "Department"),
    ]

    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    description = models.TextField()
    org_type = models.CharField(max_length=20, choices=ORG_TYPES)
    logo = models.ImageField(upload_to="org_logos/", null=True, blank=True)
    cover_image = models.ImageField(upload_to="org_covers/", null=True, blank=True)
    is_active = models.BooleanField(default=True)
    member_count = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "organizations"
        ordering = ["name", "-created_at"]
        indexes = [
            models.Index(fields=["org_type", "is_active"]),
            models.Index(fields=["slug"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f"/orgs/{self.slug}/"


class OrganizationMembership(BaseModel):
    """User membership in organizations"""

    ROLES = [
        ("member", "Member"),
        ("moderator", "Moderator"),
        ("admin", "Admin"),
        ("president", "President"),
        ("vice_president", "Vice President"),
        ("secretary", "Secretary"),
        ("treasurer", "Treasurer"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("banned", "Banned"),
    ]

    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLES, default="member")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")

    class Meta:
        db_table = "organization_memberships"
        unique_together = ["user", "organization"]
        indexes = [
            models.Index(fields=["organization", "status", "role"]),
            models.Index(fields=["user", "status", "role"]),
        ]
