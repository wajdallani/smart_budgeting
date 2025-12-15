from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.conf import settings
from apps.categorieApp.models import Categorie  # adjust import path if needed

class Depense(models.Model):
    """Modèle pour gérer les dépenses"""
    user = models.ForeignKey(  # ✅ add this
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="depenses"
    )
    categorie = models.ForeignKey(
        Categorie,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="depenses",
        verbose_name="Catégorie"
    )
    depense_id = models.AutoField(
        primary_key=True,
        verbose_name="ID Dépense"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Montant"
    )
    date = models.DateField(
        verbose_name="Date"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Notes"
    )
    facture_img = models.ImageField(
        upload_to='factures/%Y/%m/',
        blank=True,
        null=True,
        verbose_name="Image de la facture"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Dépense"
        verbose_name_plural = "Dépenses"
        ordering = ['-date', '-created_at']
        
    def __str__(self):
        return f"DEP{self.depense_id:04d} - {self.amount}€"
