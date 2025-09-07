from django import forms
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from allauth.account.forms import SignupForm, LoginForm
from .models import User, Profile
import re
from django.utils import timezone
from django.utils.text import slugify
import os

from shared.forms import DaisyUIFormMixin


class CustomSignupForm(DaisyUIFormMixin, SignupForm):
    """Custom signup form to collect RUET-specific information"""

    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Enter your first name"}),
        help_text="Your legal first name as it appears on official documents",
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Enter your last name"}),
        help_text="Your legal last name as it appears on official documents",
    )
    user_type = forms.ChoiceField(
        choices=User.USER_TYPES,
        required=True,
        initial="student",
        help_text="Select your role at RUET",
    )
    department = forms.ChoiceField(
        choices=User.DEPARTMENTS,
        required=True,
        help_text="Your academic department at RUET",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Update email field
        self.fields["email"].widget.attrs.update(
            {"placeholder": "Enter your email address"}
        )
        self.fields["email"].help_text = "Use your institutional email if available"

        # Update password fields
        self.fields["password1"].widget.attrs.update(
            {"placeholder": "Create a strong password"}
        )
        self.fields["password1"].help_text = "Must be at least 8 characters long"

        self.fields["password2"].widget.attrs.update(
            {"placeholder": "Confirm your password"}
        )
        self.fields["password2"].help_text = "Enter the same password again"

    def save(self, request):
        user = super().save(request)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.user_type = self.cleaned_data["user_type"]
        user.department = self.cleaned_data["department"]
        user.save()
        return user


class CustomLoginForm(DaisyUIFormMixin, LoginForm):
    """Custom login form with DaisyUI styling"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["login"].widget.attrs.update(
            {"placeholder": "Enter your username or email"}
        )
        self.fields["login"].help_text = "Use the email or username you registered with"

        self.fields["password"].widget.attrs.update(
            {"placeholder": "Enter your password"}
        )

        # Make the remember checkbox prettier
        if "remember" in self.fields:
            self.fields["remember"].help_text = "Keep me signed in on this device"


class UserUpdateForm(DaisyUIFormMixin, forms.ModelForm):
    """Form for updating basic user information"""

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "student_id",
            "user_type",
            "department",
            "series",
        ]
        widgets = {
            "first_name": forms.TextInput(attrs={"placeholder": "First Name"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Last Name"}),
            "username": forms.TextInput(attrs={"placeholder": "Username"}),
            "email": forms.EmailInput(attrs={"placeholder": "Email Address"}),
            "student_id": forms.TextInput(attrs={"placeholder": "Student/Employee ID"}),
            "series": forms.TextInput(attrs={"placeholder": "Series (e.g., 2019)"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make email readonly if user has verified email
        if (
            self.instance
            and self.instance.emailaddress_set.filter(verified=True).exists()
        ):
            self.fields["email"].widget.attrs["readonly"] = True
            self.fields["email"].widget.attrs["class"] += " input-disabled"
            self.fields[
                "email"
            ].help_text = (
                "Email is verified and cannot be changed. Contact admin if needed."
            )

    def clean_username(self):
        username = self.cleaned_data["username"]
        if not re.match(r"^[a-zA-Z0-9_]+$", username):
            raise ValidationError(
                "Username can only contain letters, numbers, and underscores."
            )

        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise ValidationError("This username is already taken.")

        return username

    def save(self, commit=True):
        try:
            return super().save(commit=commit)
        except IntegrityError as e:
            if "username" in str(e).lower():
                raise ValidationError(
                    "This username is already taken. Please choose another."
                )
            raise

    def clean_student_id(self):
        student_id = self.cleaned_data.get("student_id")
        if student_id:
            if (
                User.objects.filter(student_id=student_id)
                .exclude(pk=self.instance.pk)
                .exists()
            ):
                raise ValidationError("This Student is already registered.")
        return student_id

    def clean_series(self):
        series = self.cleaned_data.get("series")
        user_type = self.cleaned_data.get("user_type")

        if user_type == "student" and series:
            try:
                series_year = int(series)
                current_year = timezone.now().year
                if series_year < 2000 or series_year > current_year + 1:
                    raise ValidationError("Please enter a valid series year.")
            except ValueError:
                raise ValidationError("Series must be a valid year.")

        return series


class AvatarUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["avatar"]
        widgets = {
            "avatar": forms.FileInput(
                attrs={
                    "class": "form-file-input",
                    "accept": "image/*",
                    "hx-post": "",
                    "hx-trigger": "change",
                    "hx-target": "#avatar-preview",
                    "hx-swap": "outerHTML",
                    "hx-headers": '{"X-CSRFToken": "{{ csrf_token }}"}',
                }
            )
        }

    def clean_avatar(self):
        avatar = self.cleaned_data.get("avatar")
        if avatar:
            # Check file size (5MB limit)
            if avatar.size > 5 * 1024 * 1024:
                raise ValidationError("Image file too large. Maximum size is 5MB.")

            # Check file type
            if not avatar.content_type.startswith("image/"):
                raise ValidationError("Please upload a valid image file.")

            # Validate image dimensions to prevent extremely large images
            try:
                from PIL import Image

                with Image.open(avatar) as img:
                    if img.width > 4096 or img.height > 4096:
                        raise ValidationError(
                            "Image dimensions too large. Maximum size is 4096x4096 pixels."
                        )
            except Exception:
                # If PIL fails, still allow the upload but log the issue
                pass

            # Generate safe filename
            user = self.instance.user if hasattr(self.instance, "user") else None
            if user:
                username = slugify(user.username)
                ext = os.path.splitext(avatar.name)[1]
                if user.student_id:
                    new_filename = f"{username}_{user.student_id}{ext}"
                else:
                    new_filename = f"{username}_{user.id}{ext}"
                avatar.name = new_filename

        return avatar


class ProfileUpdateForm(DaisyUIFormMixin, forms.ModelForm):
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"placeholder": "Tell us about yourself..."}),
    )

    birth_date = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                "type": "date",
            }
        ),
    )

    facebook_url = forms.URLField(
        required=False,
        widget=forms.URLInput(
            attrs={
                "placeholder": "https://facebook.com/username",
            }
        ),
    )
    linkedin_url = forms.URLField(
        required=False,
        widget=forms.URLInput(
            attrs={
                "placeholder": "https://linkedin.com/in/username",
            }
        ),
    )
    github_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={"placeholder": "https://github.com/username"}),
    )
    twitter_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={"placeholder": "https://twitter.com/username"}),
    )

    interests_text = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "programming, robotics, AI (comma-separated)",
            }
        ),
    )
    skills_text = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Python, Django, JavaScript (comma-separated)",
            }
        ),
    )

    class Meta:
        model = Profile
        fields = ["phone", "address", "birth_date", "show_email", "show_phone", "bio"]
        widgets = {
            "phone": forms.TextInput(attrs={"placeholder": "+880 1XXX-XXXXXX"}),
            "address": forms.Textarea(
                attrs={
                    "placeholder": "Your address...",
                    "rows": 3,
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.social_links:
            self.fields["facebook_url"].initial = self.instance.social_links.get(
                "facebook", ""
            )
            self.fields["linkedin_url"].initial = self.instance.social_links.get(
                "linkedin", ""
            )
            self.fields["github_url"].initial = self.instance.social_links.get(
                "github", ""
            )
            self.fields["twitter_url"].initial = self.instance.social_links.get(
                "twitter", ""
            )

        if self.instance and self.instance.interests:
            self.fields["interests_text"].initial = ", ".join(self.instance.interests)

        if self.instance and self.instance.skills:
            self.fields["skills_text"].initial = ", ".join(self.instance.skills)

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if phone:
            phone_pattern = r"^(\+880|880|0)?[1-9]\d{8,10}$"
            if not re.match(phone_pattern, phone):
                raise ValidationError("Please enter a valid phone number.")
        return phone

    def save(self, commit=True):
        profile = super().save(commit=False)

        birth_date = self.cleaned_data.get("birth_date")
        if birth_date:
            profile.birth_date = birth_date

        social_links = {}
        for platform in ["facebook", "linkedin", "github", "twitter"]:
            url = self.cleaned_data.get(f"{platform}_url")
            if url:
                social_links[platform] = url
        profile.social_links = social_links

        interests_text = self.cleaned_data.get("interests_text", "")
        if interests_text:
            interests = [
                interest.strip()
                for interest in interests_text.split(",")
                if interest.strip()
            ]
            profile.interests = interests
        else:
            profile.interests = []

        skills_text = self.cleaned_data.get("skills_text", "")
        if skills_text:
            skills = [
                skill.strip() for skill in skills_text.split(",") if skill.strip()
            ]
            profile.skills = skills
        else:
            profile.skills = []

        if commit:
            profile.save()
        return profile


class PasswordChangeForm(DaisyUIFormMixin, forms.Form):
    """Custom password change form with better validation"""

    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Current Password"})
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "New Password"}),
        help_text="Password must be at least 8 characters long.",
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Confirm New Password"})
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current_password = self.cleaned_data["current_password"]
        if not self.user.check_password(current_password):
            raise ValidationError("Current password is incorrect.")
        return current_password

    def clean_new_password2(self):
        password1 = self.cleaned_data.get("new_password1")
        password2 = self.cleaned_data.get("new_password2")

        if password1 and password2:
            if password1 != password2:
                raise ValidationError("The two password fields didn't match.")

        if len(password1) < 8:
            raise ValidationError("Password must be at least 8 characters long.")

        return password2

    def save(self):
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        self.user.save()
        return self.user
