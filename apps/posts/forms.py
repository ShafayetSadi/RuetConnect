from django import forms

from apps.posts.models import Post


class PostForm(forms.ModelForm):
    # Explicitly define the visibility field with choices
    visibility = forms.ChoiceField(
        choices=[
            ("thread", "Thread Members Only"),
            ("organization", "Organization Members"),
            ("public", "Public"),
        ],
        initial="thread",
        help_text="Who can see this post?",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = Post
        fields = [
            "thread",
            "title",
            "content",
            "post_type",
            "visibility",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-input"}),
            "content": forms.Textarea(attrs={"class": "form-textarea", "rows": 5}),
            "post_type": forms.Select(attrs={"class": "form-select"}),
            "thread": forms.Select(attrs={"class": "form-select"}),
        }
