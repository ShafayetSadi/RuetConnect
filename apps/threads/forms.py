from django import forms

from apps.threads.models import Thread


class ThreadForm(forms.ModelForm):
    class Meta:
        model = Thread
        fields = ["title", "description", "thread_type", "organization"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-input"}),
            "description": forms.Textarea(
                attrs={"class": "form-textarea", "rows": 4}
            ),
            "thread_type": forms.Select(attrs={"class": "form-select"}),
            "organization": forms.Select(attrs={"class": "form-select"}),
        }
