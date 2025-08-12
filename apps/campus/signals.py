from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.campus.models import OrganizationMembership


@receiver([post_save, post_delete], sender=OrganizationMembership)
def update_member_count(sender, instance: OrganizationMembership, **kwargs):
    org = instance.organization
    active_count = (
        OrganizationMembership.objects.filter(organization=org, status="active").count()
    )
    org.member_count = active_count
    org.save(update_fields=["member_count", "updated_at"])