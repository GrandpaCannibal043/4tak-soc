from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from captcha.fields import CaptchaField
from .models import RegistrationCode, Profile
from .models import Project, Profile


class ProjectForm(forms.ModelForm):

    mentor = forms.ModelChoiceField(
        queryset=User.objects.filter(profile__role='teacher'),
        required=False,
        widget=forms.Select(attrs={
            "class": "form-select"
        })
    )

    class Meta:
        model = Project
        fields = [
            "title",
            "functionality",
            "school_class",
            "project_type",
            "difficulty",
            "mentor",
            "image",
            "documentation_pdf",
            'video_url',
        ]

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
            "school_class": forms.Select(attrs={
                "class": "form-select"
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
            "documentation_pdf": forms.ClearableFileInput(attrs={
                "class": "form-control",
                "accept": ".pdf"
            }),
            'video_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': ''
            }),
        }


class CustomUserCreationForm(UserCreationForm):
    captcha = CaptchaField()
    registration_code = forms.CharField(
        max_length=12,
        label="Registračný kód"
    )

    class Meta:
        model = User
        fields = ("username", "password1", "password2", "registration_code", "captcha")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "form-control"
            })

    def clean_registration_code(self):
        code = self.cleaned_data.get("registration_code")

        try:
            reg_code = RegistrationCode.objects.get(code=code, used=False)
        except RegistrationCode.DoesNotExist:
            raise forms.ValidationError("Neplatný alebo už použitý registračný kód.")

        self.reg_code_obj = reg_code
        return code

    def save(self, commit=True):
        user = super().save(commit)

        # Nastavenie role podľa kódu
        Profile.objects.create(
            user=user,
            role=self.reg_code_obj.role
        )

        # Označiť kód ako použitý
        self.reg_code_obj.used = True
        self.reg_code_obj.save()

        return user

