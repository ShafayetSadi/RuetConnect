from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import Profile, User


class CreateUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class UpdateUserForm(UserChangeForm):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "password"]


class UpdateProfileForm(forms.ModelForm):
    github = forms.URLField(required=False)
    linkedin = forms.URLField(required=False)
    facebook = forms.URLField(required=False)
    twitter = forms.URLField(required=False)
    instagram = forms.URLField(required=False)

    class Meta:
        model = Profile
        fields = [
            "bio",
            "birth_date",
            "image",
            "address",
            "city",
            "country",
            "social_links",
        ]

    def __init__(self, *args, **kwargs):
        super(UpdateProfileForm, self).__init__(*args, **kwargs)
        social_links = self.instance.social_links or {}
        self.fields["github"].initial = social_links.get("github", "")
        self.fields["linkedin"].initial = social_links.get("linkedin", "")
        self.fields["facebook"].initial = social_links.get("facebook", "")
        self.fields["twitter"].initial = social_links.get("twitter", "")
        self.fields["instagram"].initial = social_links.get("instagram", "")

    def save(self, commit=True):
        social_links = {
            "github": self.cleaned_data.get("github", ""),
            "linkedin": self.cleaned_data.get("linkedin", ""),
            "facebook": self.cleaned_data.get("facebook", ""),
            "twitter": self.cleaned_data.get("twitter", ""),
            "instagram": self.cleaned_data.get("instagram", ""),
        }
        self.instance.social_links = social_links
        return super(UpdateProfileForm, self).save(commit=commit)
