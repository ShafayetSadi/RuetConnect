from django import forms
from django.core.exceptions import ValidationError
import re

from apps.campus.models import Organization, OrganizationMembership
from shared.forms import DaisyUIFormMixin


class OrganizationForm(DaisyUIFormMixin, forms.ModelForm):
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
            "name": forms.TextInput(attrs={"placeholder": "Enter organization name"}),
            "description": forms.Textarea(
                attrs={
                    "placeholder": "Describe your organization, its mission and activities...",
                    "rows": 5
                }
            ),
            "org_type": forms.Select(),
            "logo": forms.FileInput(attrs={"accept": "image/*"}),
            "cover_image": forms.FileInput(attrs={"accept": "image/*"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add help text
        self.fields["name"].help_text = "This will be the display name for your organization"
        self.fields["description"].help_text = "Tell people what your organization is about"
        self.fields["org_type"].help_text = "Select the category that best describes your organization"
        self.fields["logo"].help_text = "Upload a logo for your organization (recommended: square image, max 5MB)"
        self.fields["cover_image"].help_text = "Upload a cover image for your organization page (recommended: 16:9 ratio, max 5MB)"
        self.fields["is_active"].help_text = "Inactive organizations won't appear in public listings"

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if name:
            # Check for minimum length
            if len(name.strip()) < 3:
                raise ValidationError("Organization name must be at least 3 characters long.")
            
            # Check for duplicate names (excluding current instance during edit)
            if self.instance.pk:
                if Organization.objects.filter(name__iexact=name).exclude(pk=self.instance.pk).exists():
                    raise ValidationError("An organization with this name already exists.")
            else:
                if Organization.objects.filter(name__iexact=name).exists():
                    raise ValidationError("An organization with this name already exists.")
        
        return name

    def clean_description(self):
        description = self.cleaned_data.get("description")
        if description and len(description.strip()) < 20:
            raise ValidationError("Description must be at least 20 characters long.")
        return description

    def clean_logo(self):
        logo = self.cleaned_data.get("logo")
        if logo:
            if logo.size > 5 * 1024 * 1024:  # 5MB limit
                raise ValidationError("Logo file too large. Maximum size is 5MB.")
            
            if not logo.content_type.startswith("image/"):
                raise ValidationError("Please upload a valid image file for the logo.")
        
        return logo

    def clean_cover_image(self):
        cover_image = self.cleaned_data.get("cover_image")
        if cover_image:
            if cover_image.size > 5 * 1024 * 1024:  # 5MB limit
                raise ValidationError("Cover image file too large. Maximum size is 5MB.")
            
            if not cover_image.content_type.startswith("image/"):
                raise ValidationError("Please upload a valid image file for the cover image.")
        
        return cover_image


class OrganizationMembershipForm(DaisyUIFormMixin, forms.ModelForm):
    class Meta:
        model = OrganizationMembership
        fields = ["organization", "role", "status"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add help text
        self.fields["organization"].help_text = "Select the organization you want to join"
        self.fields["role"].help_text = "Choose your role in the organization"
        self.fields["status"].help_text = "Membership status (pending approval by default)"

    def save(self, user, commit=True):
        membership = super().save(commit=False)
        membership.user = user
        if commit:
            membership.save()
        return membership
