from django import forms

from apps.campus.models import Organization, OrganizationMembership


class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = [
            "name",
            "description",
            "org_type",
            "logo",
            "cover_image",
            "is_active",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-input"}),
            "description": forms.Textarea(
                attrs={"class": "form-textarea", "rows": 5}
            ),
            "org_type": forms.Select(attrs={"class": "form-select"}),
        }


class OrganizationMembershipForm(forms.ModelForm):
    class Meta:
        model = OrganizationMembership
        fields = ["organization", "role", "status"]
        widgets = {
            "organization": forms.Select(attrs={"class": "form-select"}),
            "role": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }

    def save(self, user, commit=True):
        membership = super().save(commit=False)
        membership.user = user
        if commit:
            membership.save()
        return membership
