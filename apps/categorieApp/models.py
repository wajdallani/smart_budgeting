from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Categorie(models.Model):
    nom = models.CharField(max_length=100, verbose_name="Nom de la catégorie")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    est_globale = models.BooleanField(default=False, verbose_name="Catégorie globale")
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='categories',
        verbose_name="Créateur"
    )
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['-date_creation']
        unique_together = [['nom', 'utilisateur']]

    def __str__(self):
        if self.est_globale:
            return f"{self.nom} (Globale)"
        display = getattr(self.utilisateur, "username", None) or getattr(self.utilisateur, "email", None) or str(self.utilisateur)

        return f"{self.nom} ({display})"

    def peut_etre_modifiee_par(self, user):
        """Vérifie si l'utilisateur peut modifier cette catégorie"""
        if user.is_staff:
            return True
        return self.utilisateur == user and not self.est_globale

    def peut_etre_supprimee_par(self, user):
        """Vérifie si l'utilisateur peut supprimer cette catégorie"""
        if user.is_staff and self.est_globale:
            return True
        return self.utilisateur == user and not self.est_globale

