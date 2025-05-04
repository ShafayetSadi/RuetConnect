from allauth.account.signals import email_confirmed
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile, User


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    # if user is created, create profile
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    # if user is saved, save profile
    instance.profile.save()


@receiver(email_confirmed)
def email_verified_handler(request, email_address, **kwargs):
    """When a user confirms their email, set the is_email_verified field to True."""
    user = email_address.user
    user.is_email_verified = True
    user.save()
