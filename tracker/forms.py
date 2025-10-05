from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from datetime import datetime

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("هذا البريد الإلكتروني مستخدم بالفعل")
        return email

class StudyPlanForm(forms.Form):
    start_date = forms.DateField(
        label="تاريخ بداية الخطة",
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=datetime(2025, 10, 1)
    )
    end_date = forms.DateField(
        label="تاريخ نهاية الخطة",
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=datetime(2026, 10, 1)
    )