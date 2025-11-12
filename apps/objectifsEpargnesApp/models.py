from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator
from django.core.exceptions import ValidationError

User = get_user_model()
# Custom validators
def validate_future_date(value):
    """Ensure the target_date or added_at is not in the past."""
    if value < timezone.now().date():
        raise ValidationError("La date ne peut pas être dans le passé.")


def validate_positive_amount(value):
    """Ensure that amounts are strictly positive."""
    if value <= 0:
        raise ValidationError("Le montant doit être supérieur à 0.")


class ObjEpargne(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('ACHIEVED', 'Achieved'),
        ('CANCELLED', 'Cancelled'),
    ]

    goal_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saving_goals')
    name = models.CharField(
        max_length=100,
        validators=[MinLengthValidator(3, message="Le nom doit contenir au moins 3 caractères.")]
    )
    target_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[validate_positive_amount, MaxValueValidator(1_000_000, message="Le montant ne peut pas dépasser 1 000 000.")]
    )
    target_date = models.DateField(
        blank=True,
        null=True,
        validators=[validate_future_date]
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='ACTIVE'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['status', 'target_date']
        verbose_name = 'Objectif Epargne'
        verbose_name_plural = 'Objectif Epargnes'

    def __str__(self):
        return f"{self.name} ({self.status})"

    @property
    def total_contributed(self):
        """Sum of all contributions linked to this goal"""
        total = self.contributions.aggregate(models.Sum('amount'))['amount__sum']
        return total or 0

    @property
    def progress_percentage(self):
        """Return percentage of target amount saved"""
        if self.target_amount > 0:
            return round((self.total_contributed / self.target_amount) * 100, 2)
        return 0


class ObjEpargneContribution(models.Model):
    cont_id = models.AutoField(primary_key=True)
    goal = models.ForeignKey(ObjEpargne, on_delete=models.CASCADE, related_name='contributions')
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[validate_positive_amount]
    )
    added_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-added_at']
        verbose_name = 'Objectif Epargne Contribution'
        verbose_name_plural = 'Objectif Epargnes Contributions'

    def __str__(self):
        return f"{self.amount} added to {self.goal.name}"
