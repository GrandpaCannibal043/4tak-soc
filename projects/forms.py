from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Project
from captcha.fields import CaptchaField


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["title", "functionality", "project_type", "difficulty", "image"]

        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Názov projektu"
            }),
            "functionality": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "Stručný opis funkcionality projektu"
            }),
            "project_type": forms.Select(attrs={
                "class": "form-select"
            }),
            "difficulty": forms.Select(attrs={
                "class": "form-select"
            }),
            "image": forms.ClearableFileInput(attrs={
                "class": "form-control"
            }),
        }

class CustomUserCreationForm(UserCreationForm):
    captcha = CaptchaField()
    class Meta:
        model = User
        fields = ("username", "password1", "password2", "captcha")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "form-control"
                
            })