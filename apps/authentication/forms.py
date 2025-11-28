# apps/authentication/forms.py
from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import re

User = get_user_model()


class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '············',
            'id': 'password',
            'aria-describedby': 'password'
        }),
        label='Mot de passe',
        min_length=8,
        help_text='Le mot de passe doit contenir au moins 8 caractères',
        required=True
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '············',
            'id': 'password-confirm',
            'aria-describedby': 'password-confirm'
        }),
        label='Confirmer le mot de passe',
        required=True
    )

    class Meta:
        model = User
        fields = ['firstname', 'lastname', 'email']
        widgets = {
            'firstname': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Entrez votre prénom',
                'id': 'firstname',
                'autofocus': True
            }),
            'lastname': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Entrez votre nom',
                'id': 'lastname'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Entrez votre email',
                'id': 'email'
            }),
        }
        labels = {
            'firstname': 'Prénom',
            'lastname': 'Nom',
            'email': 'Email',
        }

    def clean_firstname(self):
        firstname = self.cleaned_data.get('firstname')
        if not re.match(r'^[a-zA-ZÀ-ÿ\s\-\']+$', firstname):
            raise ValidationError(
                'Le prénom ne peut contenir que des lettres, espaces, tirets et apostrophes.'
            )
        return firstname

    def clean_lastname(self):
        lastname = self.cleaned_data.get('lastname')
        if not re.match(r'^[a-zA-ZÀ-ÿ\s\-\']+$', lastname):
            raise ValidationError(
                'Le nom ne peut contenir que des lettres, espaces, tirets et apostrophes.'
            )
        return lastname

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Cette adresse email est déjà utilisée.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            raise ValidationError('Les mots de passe ne correspondent pas.')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.role = 'utilisateur'  # Par défaut
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Entrez votre email',
            'id': 'email',
            'autofocus': 'autofocus'
        }),
        label='Email'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '············',
            'id': 'password'
        }),
        label='Mot de passe'
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'remember-me'
        }),
        label='Se souvenir de moi'
    )