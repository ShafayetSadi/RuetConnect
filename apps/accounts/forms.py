from allauth.account.forms import SignupForm
from django import forms

from .models import Profile, User


class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label="First Name")
    last_name = forms.CharField(max_length=30, label="Last Name")

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email"]


class UpdateProfileForm(forms.ModelForm):
    github = forms.URLField(required=False, label="GitHub Profile URL")
    linkedin = forms.URLField(required=False, label="LinkedIn Profile URL")
    facebook = forms.URLField(required=False, label="Facebook Profile URL")
    twitter = forms.URLField(required=False, label="Twitter Profile URL")
    instagram = forms.URLField(required=False, label="Instagram Profile URL")

    class Meta:
        model = Profile
        fields = [
            "bio",
            "birth_date",
            "image",
        ]
        widgets = {"birth_date": forms.DateInput(attrs={"type": "date"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.social_links:
            social_links = self.instance.social_links
            self.fields["github"].initial = social_links.get("github", "")
            self.fields["linkedin"].initial = social_links.get("linkedin", "")
            self.fields["facebook"].initial = social_links.get("facebook", "")
            self.fields["twitter"].initial = social_links.get("twitter", "")
            self.fields["instagram"].initial = social_links.get("instagram", "")

    def save(self, commit=True):
        profile = super().save(commit=False)
        profile.social_links = {
            "github": self.cleaned_data.get("github", ""),
            "linkedin": self.cleaned_data.get("linkedin", ""),
            "facebook": self.cleaned_data.get("facebook", ""),
            "twitter": self.cleaned_data.get("twitter", ""),
            "instagram": self.cleaned_data.get("instagram", ""),
        }
        if commit:
            profile.save()
        return profile
