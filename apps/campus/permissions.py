from typing import Iterable

from apps.campus.models import Organization, OrganizationMembership

ORG_STAFF_ROLES: set[str] = {
    "admin",
    "president",
    "vice_president",
    "secretary",
    "moderator",
}


def user_membership(user, organization: Organization) -> OrganizationMembership | None:
    if not user.is_authenticated:
        return None
    return (
        OrganizationMembership.objects.select_related("organization", "user")
        .filter(user=user, organization=organization)
        .first()
    )


def is_org_member(user, organization: Organization) -> bool:
    membership = user_membership(user, organization)
    return bool(membership and membership.status == "active")


def is_org_staff(user, organization: Organization) -> bool:
    membership = user_membership(user, organization)
    return bool(
        membership and membership.status == "active" and membership.role in ORG_STAFF_ROLES
    )


def require_any_role(user, organization: Organization, roles: Iterable[str]) -> bool:
    membership = user_membership(user, organization)
    return bool(membership and membership.status == "active" and membership.role in set(roles))
