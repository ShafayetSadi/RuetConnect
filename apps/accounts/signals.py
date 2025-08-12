from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile, User


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """Create Profile when User is created"""
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    """Save Profile when User is saved"""
    if hasattr(instance, "profile"):
        instance.profile.save()
