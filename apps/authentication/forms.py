# apps/authentication/forms.py
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm
from django.core.exceptions import ValidationError
import re

User = get_user_model()


class CustomPasswordResetForm(PasswordResetForm):
    """
    Formulaire personnalisé qui vérifie si l'email existe
    """
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Entrez votre email',
            'id': 'email',
            'autofocus': True
        }),
        label='Email'
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        # Vérifier si l'utilisateur existe
        if not User.objects.filter(email=email).exists():
            raise ValidationError(
                "Désolé, nous n'avons pas trouvé de compte associé à cette adresse email. "
                "Veuillez vous inscrire d'abord."
            )
        
        # Vérifier si l'utilisateur est actif
        user = User.objects.get(email=email)
        if not user.is_active:
            raise ValidationError(
                "Votre compte n'est pas encore activé. "
                "Veuillez vous inscrire à nouveau pour recevoir un nouveau code de vérification."
            )
        
        return email


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
        
        # 🔹 Vérifier si un utilisateur avec cet email existe
        existing_users = User.objects.filter(email=email)
        
        if existing_users.exists():
            user = existing_users.first()
            
            # 🔹 Si le compte est INACTIF, on permet la réinscription
            if not user.is_active:
                # On va réutiliser ce compte au lieu d'en créer un nouveau
                self.existing_inactive_user = user
                return email
            else:
                # Si le compte est ACTIF, on refuse
                raise ValidationError(
                    'Cette adresse email est déjà utilisée par un compte actif. '
                    'Veuillez vous connecter ou réinitialiser votre mot de passe.'
                )
        
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            raise ValidationError('Les mots de passe ne correspondent pas.')

        return cleaned_data

    def save(self, commit=True):
        # 🔹 Si un compte inactif existe, on le met à jour au lieu d'en créer un nouveau
        if hasattr(self, 'existing_inactive_user'):
            user = self.existing_inactive_user
            user.firstname = self.cleaned_data['firstname']
            user.lastname = self.cleaned_data['lastname']
            user.set_password(self.cleaned_data['password'])
            user.role = 'utilisateur'
            user.is_active = False
            user.is_email_verified = False
            user.email_verification_code = None
            user.verification_code_created_at = None
            
            if commit:
                user.save()
            
            # Marquer qu'on a réutilisé un compte
            self.reused_account = True
            return user
        else:
            # 🔹 Créer un nouveau compte normalement
            user = super().save(commit=False)
            user.set_password(self.cleaned_data['password'])
            user.role = 'utilisateur'
            user.is_active = False
            user.is_email_verified = False
            
            if commit:
                user.save()
            
            self.reused_account = False
            return user


class VerificationCodeForm(forms.Form):
    code = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control text-center',
            'placeholder': '000000',
            'maxlength': '6',
            'pattern': '[0-9]{6}',
            'inputmode': 'numeric'
        }),
        label='Code de vérification'
    )

    def clean_code(self):
        code = self.cleaned_data.get('code')
        if not code.isdigit():
            raise ValidationError("Le code doit contenir uniquement des chiffres.")
        return code

    def clean_code(self):
        code = self.cleaned_data.get('code')
        if not code.isdigit():
            raise ValidationError("Le code doit contenir uniquement des chiffres.")
        return code

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
