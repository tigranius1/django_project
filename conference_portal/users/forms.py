from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
import re
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        label='Логин',
        min_length=6,
        help_text='Только латиница и цифры, не менее 6 символов'
    )
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput,
        min_length=8
    )
    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput
    )
    full_name = forms.CharField(label='ФИО', max_length=255, required=False)
    phone = forms.CharField(
        label='Телефон',
        max_length=20,
        help_text='Формат: 8(XXX)XXX-XX-XX',
        required=False,
    )
    email = forms.EmailField(label='Электронная почта')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not re.match(r'^[a-zA-Z0-9]+$', username):
            raise ValidationError('Логин должен содержать только латиницу и цифры')
        if len(username) < 6:
            raise ValidationError('Логин должен быть не менее 6 символов')
        return username

    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name')
        if full_name and not all(c.isalpha() or c.isspace() for c in full_name):
            raise ValidationError('ФИО должно содержать только символы кириллицы и пробелы')
        return full_name

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not re.match(r'^8\(\d{3}\)\d{3}-\d{2}-\d{2}$', phone):
            raise ValidationError('Телефон должен быть в формате 8(XXX)XXX-XX-XX')
        return phone

    class Meta:
        model = CustomUser
        fields = ('username', 'password1', 'password2', 'full_name', 'phone', 'email')