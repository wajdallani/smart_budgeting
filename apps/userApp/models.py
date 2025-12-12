# apps/userApp/models.py
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
import re
import random
import string


def validate_no_special_chars(value):
    """Valide que le champ ne contient pas de caractères spéciaux ni de chiffres"""
    if not re.match(r'^[a-zA-ZÀ-ÿ\s\-\']+$', value):
        raise ValidationError(
            'Ce champ ne peut contenir que des lettres, espaces, tirets et apostrophes.'
        )


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'adresse email est obligatoire")
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_email_verified', True)
        extra_fields.setdefault('is_active', True)  # 🔹 Superuser actif par défaut

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser doit avoir is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser doit avoir is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('utilisateur', 'Utilisateur'),
    ]

    email = models.EmailField(
        verbose_name='Adresse email',
        max_length=255,
        unique=True,
        validators=[EmailValidator(message="Veuillez entrer une adresse email valide")]
    )
    firstname = models.CharField(
        verbose_name='Prénom',
        max_length=100,
        validators=[validate_no_special_chars]
    )
    lastname = models.CharField(
        verbose_name='Nom',
        max_length=100,
        validators=[validate_no_special_chars]
    )
    role = models.CharField(
        verbose_name='Rôle',
        max_length=20,
        choices=ROLE_CHOICES,
        default='utilisateur'
    )

    # 🔹 Champs de vérification email
    is_email_verified = models.BooleanField(
        verbose_name='Email vérifié',
        default=False
    )
    email_verification_code = models.CharField(
        verbose_name='Code de vérification',
        max_length=6,
        blank=True,
        null=True
    )
    verification_code_created_at = models.DateTimeField(
        verbose_name='Date de création du code',
        blank=True,
        null=True
    )

    # Relation N-N métier User ↔ AppGroup via GroupMembre
    member_groups = models.ManyToManyField(
        'AppGroup',
        through='GroupMembre',
        related_name='members',
        blank=True,
        verbose_name='Groupes'
    )
    
    # 🔹 MODIFICATION : is_active = False par défaut
    is_active = models.BooleanField(
        verbose_name='Compte actif',
        default=False,  # ← Compte INACTIF par défaut jusqu'à vérification
        help_text='Le compte devient actif uniquement après vérification de l\'email'
    )
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['firstname', 'lastname']

    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.firstname} {self.lastname} ({self.email})"

    def get_full_name(self):
        return f"{self.firstname} {self.lastname}"

    def get_short_name(self):
        return self.firstname

    @property
    def is_admin(self):
        return self.role == 'admin'

    def generate_verification_code(self):
        """Génère un code de vérification à 6 chiffres"""
        code = ''.join(random.choices(string.digits, k=6))
        self.email_verification_code = code
        self.verification_code_created_at = timezone.now()
        self.save(update_fields=['email_verification_code', 'verification_code_created_at'])
        return code

    def is_verification_code_valid(self, code, expiry_minutes=10):
        """Vérifie si le code est valide et non expiré"""
        if not self.email_verification_code or not self.verification_code_created_at:
            return False
        
        if self.email_verification_code != code:
            return False
        
        expiry_time = self.verification_code_created_at + timedelta(minutes=expiry_minutes)
        return timezone.now() <= expiry_time

    def verify_email(self):
        """
        Marque l'email comme vérifié, active le compte et nettoie le code
        🔹 MODIFICATION : Active également le compte
        """
        self.is_email_verified = True
        self.is_active = True  # ← Active le compte
        self.email_verification_code = None
        self.verification_code_created_at = None
        self.save(update_fields=[
            'is_email_verified', 
            'is_active',  # ← Ajouté
            'email_verification_code', 
            'verification_code_created_at'
        ])


class AppGroup(models.Model):
    """
    Groupe métier (rien à voir avec les groupes de permissions Django)
    Attributs : id, name, created_at, nb_membre
    """
    name = models.CharField("Nom du groupe", max_length=150, unique=True)
    created_at = models.DateTimeField("Date de création", auto_now_add=True)
    nb_membre = models.PositiveIntegerField("Nombre de membres", default=0)

    class Meta:
        verbose_name = "Groupe"
        verbose_name_plural = "Groupes"
        ordering = ["name"]

    def __str__(self):
        return self.name


class GroupMembre(models.Model):
    """
    Table d'association entre User et AppGroup
    + date d'adhésion
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(AppGroup, on_delete=models.CASCADE)
    joined_at = models.DateTimeField("Date d'adhésion", auto_now_add=True)

    class Meta:
        unique_together = ('user', 'group')
        verbose_name = "Membre de groupe"
        verbose_name_plural = "Membres de groupe"

    def __str__(self):
        return f"{self.user.get_full_name()} → {self.group.name} (depuis {self.joined_at:%Y-%m-%d})"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            AppGroup.objects.filter(pk=self.group_id).update(
                nb_membre=models.F('nb_membre') + 1
            )

    def delete(self, *args, **kwargs):
        group_id = self.group_id
        super().delete(*args, **kwargs)
        if group_id:
            AppGroup.objects.filter(pk=group_id, nb_membre__gt=0).update(
                nb_membre=models.F('nb_membre') - 1
            )