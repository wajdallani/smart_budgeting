# apps/userApp/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from django.utils.html import format_html
from django import forms
from .models import User
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone


class UserCreationForm(forms.ModelForm):
    """
    Formulaire pour créer de nouveaux utilisateurs dans l'admin
    avec contrôles de saisie personnalisés + message global.
    """
    password1 = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Mot de passe',
            'class': 'vTextField',
            'autocomplete': 'new-password',
            'required': 'required',
            'minlength': '8',
        })
    )
    password2 = forms.CharField(
        label='Confirmation du mot de passe',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirmer le mot de passe',
            'class': 'vTextField',
            'autocomplete': 'new-password',
            'required': 'required',
            'minlength': '8',
        })
    )

    class Meta:
        model = User
        fields = ('email', 'firstname', 'lastname', 'role')
        widgets = {
            'email': forms.EmailInput(attrs={
                'placeholder': 'exemple@domaine.com',
                'class': 'vTextField',
                'required': 'required',
            }),
            'firstname': forms.TextInput(attrs={
                'placeholder': 'Prénom',
                'class': 'vTextField',
                'required': 'required',
            }),
            'lastname': forms.TextInput(attrs={
                'placeholder': 'Nom',
                'class': 'vTextField',
                'required': 'required',
            }),
            # ⚠️ IMPORTANT : on NE force PAS de widget pour "role"
            # si ton modèle a des choices, Django utilisera un <select> adapté
        }

    required_fields = ('email', 'firstname', 'lastname', 'role', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Champs requis côté Django
        for field_name in self.required_fields:
            if field_name in self.fields:
                self.fields[field_name].required = True

    # =============== VALIDATIONS PAR CHAMP ==================

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower()
        if not email:
            raise ValidationError("L'email est obligatoire.")
        if User.objects.filter(email=email).exists():
            raise ValidationError("Cet email est déjà utilisé.")
        return email

    def clean_firstname(self):
        firstname = (self.cleaned_data.get("firstname") or "").strip()
        if not firstname:
            raise ValidationError("Le prénom est obligatoire.")
        if not all(c.isalpha() or c in " -'" for c in firstname):
            raise ValidationError("Le prénom doit contenir uniquement des lettres.")
        return firstname

    def clean_lastname(self):
        lastname = (self.cleaned_data.get("lastname") or "").strip()
        if not lastname:
            raise ValidationError("Le nom est obligatoire.")
        if not all(c.isalpha() or c in " -'" for c in lastname):
            raise ValidationError("Le nom doit contenir uniquement des lettres.")
        return lastname

    def clean_role(self):
        role = (self.cleaned_data.get("role") or "").strip()
        if not role:
            raise ValidationError("Le rôle est obligatoire.")
        return role

    def clean_password1(self):
        pwd = self.cleaned_data.get("password1") or ""

        if not pwd:
            raise ValidationError("Le mot de passe est obligatoire.")
        if len(pwd) < 8:
            raise ValidationError("Le mot de passe doit contenir au moins 8 caractères.")
        if not any(c.isdigit() for c in pwd):
            raise ValidationError("Le mot de passe doit contenir au moins un chiffre.")
        if not any(c.isupper() for c in pwd):
            raise ValidationError("Le mot de passe doit contenir au moins une lettre majuscule.")
        if not any(c.islower() for c in pwd):
            raise ValidationError("Le mot de passe doit contenir au moins une lettre minuscule.")
        return pwd

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if not password2:
            raise ValidationError("Veuillez confirmer le mot de passe.")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Les mots de passe ne correspondent pas.")
        return password2

    # =============== VALIDATION GLOBALE ==================

    def clean(self):
        cleaned = super().clean()

        # Si un des champs requis est vide → message global
        missing = [f for f in self.required_fields if not cleaned.get(f)]
        if missing:
            raise ValidationError("Veuillez renseigner tous les champs.")

        return cleaned

    # =============== SAUVEGARDE ==================

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """Formulaire pour modifier les utilisateurs dans l'admin"""
    password = ReadOnlyPasswordHashField(
        label="Mot de passe",
        help_text=(
            "Les mots de passe ne sont pas stockés en clair, donc il n'y a "
            "aucun moyen de voir le mot de passe de cet utilisateur, mais vous "
            "pouvez changer le mot de passe en utilisant "
            "<a href=\"../password/\">ce formulaire</a>."
        ),
    )

    class Meta:
        model = User
        fields = ('email', 'password', 'firstname', 'lastname', 'role', 'is_active', 'is_staff', 'is_superuser')

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower()
        if not email:
            raise ValidationError("L'email est obligatoire.")
        qs = User.objects.filter(email=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Cet email est déjà utilisé par un autre utilisateur.")
        return email


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    change_list_template = 'admin/userApp/user/change_list.html'
    add_form_template = 'admin/userApp/user/add_form.html'
    change_user_password_template = "admin/userApp/user/change_password.html"

    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('email_with_avatar', 'firstname', 'lastname', 'role_badge', 'status_badge', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'role', 'date_joined')
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informations personnelles', {'fields': ('firstname', 'lastname', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates importantes', {'fields': ('date_joined', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'firstname', 'lastname', 'role', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ('date_joined', 'updated_at')
    search_fields = ('email', 'firstname', 'lastname')
    ordering = ('-date_joined',)
    filter_horizontal = ('groups', 'user_permissions',)

    # ========= LOGIQUE ACTIVER / DÉSACTIVER =========
    def changelist_view(self, request, extra_context=None):
        """
        Vue liste personnalisée :
        - gère l'activation/désactivation via AJAX (fetch)
        - injecte les stats pour le template (active_count, admin_count...)
        """
        # 1) Gestion de l'activation/désactivation via AJAX
        if (
            request.method == "POST"
            and request.headers.get("x-requested-with") == "XMLHttpRequest"
            and "user_id" in request.POST
            and "action" in request.POST
        ):
            # Vérification des permissions
            if not self.has_change_permission(request):
                return JsonResponse(
                    {"success": False, "message": "Vous n'avez pas la permission de modifier les utilisateurs."},
                    status=403
                )

            user_id = request.POST.get("user_id")
            action = request.POST.get("action")

            try:
                target_user = self.get_queryset(request).get(pk=user_id)
            except User.DoesNotExist:
                return JsonResponse(
                    {"success": False, "message": "Utilisateur introuvable."},
                    status=404
                )

            # On évite qu'un admin se désactive lui-même (optionnel mais conseillé)
            if target_user == request.user and action == "deactivate":
                return JsonResponse(
                    {"success": False, "message": "Vous ne pouvez pas désactiver votre propre compte."},
                    status=400
                )

            if action == "deactivate":
                if not target_user.is_active:
                    return JsonResponse(
                        {"success": False, "message": "Ce compte est déjà désactivé."},
                        status=400
                    )
                target_user.is_active = False
                target_user.save(update_fields=["is_active"])
                msg = f"Le compte {target_user.email} a été désactivé."
                messages.success(request, msg)
                return JsonResponse({"success": True, "message": msg})

            elif action == "activate":
                if target_user.is_active:
                    return JsonResponse(
                        {"success": False, "message": "Ce compte est déjà actif."},
                        status=400
                    )
                target_user.is_active = True
                target_user.save(update_fields=["is_active"])
                msg = f"Le compte {target_user.email} a été activé."
                messages.success(request, msg)
                return JsonResponse({"success": True, "message": msg})

            else:
                return JsonResponse(
                    {"success": False, "message": "Action non reconnue."},
                    status=400
                )

        # 2) Stats pour le header (active_count, admin_count, new_users_today)
        if extra_context is None:
            extra_context = {}

        qs = self.get_queryset(request)
        extra_context["active_count"] = qs.filter(is_active=True).count()
        extra_context["admin_count"] = qs.filter(is_superuser=True).count()
        today = timezone.now().date()
        extra_context["new_users_today"] = qs.filter(date_joined__date=today).count()

        return super().changelist_view(request, extra_context=extra_context)

    # ====== (tes méthodes existantes : email_with_avatar, role_badge, status_badge) ======
    def email_with_avatar(self, obj):
        initial = obj.email[0].upper() if obj.email else '?'
        return format_html(
            '<div style="display: flex; align-items: center; gap: 0.75rem;">'
            '<div style="width: 38px; height: 38px; border-radius: 50%; '
            'background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); '
            'display: flex; align-items: center; justify-content: center; '
            'color: white; font-weight: 600; font-size: 1rem;">{}</div>'
            '<div style="display: flex; flex-direction: column;">'
            '<span style="font-weight: 500; color: #566a7f;">{} {}</span>'
            '<span style="font-size: 0.8125rem; color: #a1acb8;">{}</span>'
            '</div>'
            '</div>',
            initial,
            obj.firstname or '',
            obj.lastname or '',
            obj.email
        )
    email_with_avatar.short_description = 'Utilisateur'

    def role_badge(self, obj):
        if obj.is_superuser:
            bg_color = '#696cff'
            text_color = 'white'
            text = 'Administrateur'
        elif obj.is_staff:
            bg_color = '#696cff'
            text_color = 'white'
            text = 'Staff'
        else:
            bg_color = '#e7e7ff'
            text_color = '#696cff'
            text = obj.role if obj.role else 'Utilisateur'
        
        return format_html(
            '<span style="padding: 0.25rem 0.625rem; border-radius: 0.25rem; '
            'font-size: 0.75rem; font-weight: 500; background: {}; color: {};">{}</span>',
            bg_color,
            text_color,
            text
        )
    role_badge.short_description = 'Rôle'

    def status_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="padding: 0.25rem 0.625rem; border-radius: 0.25rem; '
                'font-size: 0.75rem; font-weight: 500; background: #d4f4dd; color: #28c76f;">'
                '✓ Actif</span>'
            )
        else:
            return format_html(
                '<span style="padding: 0.25rem 0.625rem; border-radius: 0.25rem; '
                'font-size: 0.75rem; font-weight: 500; background: #ffe0db; color: #ff4c51;">'
                '✗ Inactif</span>'
            )
    status_badge.short_description = 'Statut'
