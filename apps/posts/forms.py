from django import forms

from apps.posts.models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            "thread",
            "title",
            "content",
            "post_type",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-input"}),
            "content": forms.Textarea(
                attrs={"class": "form-textarea", "rows": 5}
            ),
            "post_type": forms.Select(attrs={"class": "form-select"}),
            "thread": forms.Select(attrs={"class": "form-select"}),
        }
