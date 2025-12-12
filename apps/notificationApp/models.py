from django.db import models
from django.conf import settings
#user/title/message/type/link/is_read/created_at

class Notification(models.Model):
    # L’utilisateur qui reçoit la notification
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )

    # Petit titre court (ex : "Nouvel objectif atteint")
    title = models.CharField(max_length=150)

    # Message plus détaillé (optionnel)
    message = models.TextField(blank=True)

    # Type de notification (info, warning, success, etc. – utile pour le style)
    notification_type = models.CharField(
        max_length=30,
        blank=True,
        help_text="ex: info, warning, success..."
    )

    # Lien vers la page concernée (ex : détail de l’objectif, de la dépense…)
    link = models.CharField(
        max_length=255,
        blank=True,
        help_text="URL relative vers la ressource (ex: /objectifs/1/)"
    )

    # Statut : lue ou non lue
    is_read = models.BooleanField(default=False)

    # Date de création
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification pour {self.user} : {self.title}"
