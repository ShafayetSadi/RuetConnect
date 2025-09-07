from django import forms
from django.core.exceptions import ValidationError

from apps.threads.models import Thread, ThreadMembership
from apps.campus.models import Organization
from shared.forms import DaisyUIFormMixin


class ThreadForm(DaisyUIFormMixin, forms.ModelForm):
    class Meta:
        model = Thread
        fields = ["title", "description", "thread_type", "organization"]
        widgets = {
            "title": forms.TextInput(
                attrs={"placeholder": "Enter a clear and descriptive thread title"}
            ),
            "description": forms.Textarea(
                attrs={
                    "placeholder": "Describe what this thread is about, its purpose, and any relevant details...",
                    "rows": 4
                }
            ),
            "thread_type": forms.Select(),
            "organization": forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        initial = kwargs.get('initial', {})
        org = initial.get('organization', None)
        super().__init__(*args, **kwargs)

        self.fields["title"].help_text = "Choose a clear, descriptive title that summarizes your thread"
        self.fields["description"].help_text = "Provide context and details about what this thread is for"
        self.fields["thread_type"].help_text = "Select the category that best fits your thread"

        # Remove organization field if org is already set (from org_slug)
        if org:
            self.fields.pop("organization")
        else:
            self.fields["organization"].help_text = "Choose which organization this thread belongs to"
            if self.user:
                user_orgs = Organization.objects.filter(
                    organizationmembership__user=self.user, organizationmembership__status="active"
                ).distinct()
                self.fields["organization"].queryset = user_orgs
                if user_orgs.count() == 1:
                    self.fields["organization"].initial = user_orgs.first()

    def clean_title(self):
        title = self.cleaned_data.get("title")
        if title:
            # Check for minimum length
            if len(title.strip()) < 5:
                raise ValidationError(
                    "Thread title must be at least 5 characters long."
                )

            # Check for maximum length
            if len(title.strip()) > 200:
                raise ValidationError("Thread title cannot exceed 200 characters.")

            # Check for duplicate titles within the same organization
            organization = self.cleaned_data.get("organization")
            if organization:
                existing_threads = Thread.objects.filter(
                    title__iexact=title, organization=organization
                )

                # Exclude current instance during edit
                if self.instance.pk:
                    existing_threads = existing_threads.exclude(pk=self.instance.pk)

                if existing_threads.exists():
                    raise ValidationError(
                        "A thread with this title already exists in this organization."
                    )

        return title

    def clean_description(self):
        description = self.cleaned_data.get("description")
        if description and len(description.strip()) < 10:
            raise ValidationError("Description must be at least 10 characters long.")
        return description

    def clean(self):
        cleaned_data = super().clean()

        # Validate that user has permission to create threads in the selected organization
        if self.user:
            organization = cleaned_data.get("organization")
            if organization:
                from apps.campus.models import OrganizationMembership

                membership = OrganizationMembership.objects.filter(
                    user=self.user, organization=organization, status="approved"
                ).first()

                if not membership:
                    raise ValidationError(
                        "You must be an approved member of the organization to create threads."
                    )

        return cleaned_data

    def save(self, commit=True):
        thread = super().save(commit=False)

        # Set the created_by field if user is provided and thread is new
        if self.user and not thread.pk:
            thread.created_by = self.user

        if commit:
            thread.save()
        return thread


class ThreadMembershipForm(DaisyUIFormMixin, forms.ModelForm):
    class Meta:
        model = ThreadMembership
        fields = ["role"]

    def __init__(self, *args, **kwargs):
        # Extract user and thread from kwargs if provided
        self.user = kwargs.pop("user", None)
        self.thread = kwargs.pop("thread", None)
        super().__init__(*args, **kwargs)

        # Add help text
        self.fields["role"].help_text = "Select your role in this thread"

        # Restrict role choices based on user permissions
        if self.user and self.thread:
            # Check if user is an organization admin
            from apps.campus.models import OrganizationMembership

            org_membership = OrganizationMembership.objects.filter(
                user=self.user, organization=self.thread.organization, status="approved"
            ).first()

            # Limit roles based on organization membership role
            if org_membership and org_membership.role in ["admin", "moderator"]:
                # Org admins/moderators can choose any role
                pass
            else:
                # Regular members can only be thread members
                self.fields["role"].choices = [("member", "Member")]

    def clean(self):
        cleaned_data = super().clean()

        # Validate that user has permission to join the thread
        if self.user and self.thread:
            from apps.campus.models import OrganizationMembership

            org_membership = OrganizationMembership.objects.filter(
                user=self.user, organization=self.thread.organization, status="approved"
            ).first()

            if not org_membership:
                raise ValidationError(
                    "You must be an approved member of the organization to join this thread."
                )

        return cleaned_data

    def save(self, commit=True):
        membership = super().save(commit=False)

        # Set the user and thread if provided and membership is new
        if self.user and not membership.pk:
            membership.user = self.user
        if self.thread and not membership.pk:
            membership.thread = self.thread

        if commit:
            membership.save()
        return membership
