# detteApp/models.py
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.conf import settings  # IMPORTANT : utiliser le custom user model

# Create your models here.

class Debt(models.Model):
    title = models.CharField(max_length=200)  # ex: "Prêt à Paul"
    creditor = models.CharField(max_length=150, blank=True)
    debtor = models.CharField(max_length=150, blank=True)
    
    # Utilise automatiquement le User du projet
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name="dettes",
        null=True,
        blank=True
    )

    original_amount = models.DecimalField(max_digits=12, decimal_places=2)
    remaining_amount = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} — {self.remaining_amount} restant"

    def get_absolute_url(self):
        return reverse('detteApp:debt_detail', args=[str(self.pk)])

    def update_remaining(self):
        total_paid = self.payments.aggregate(total=models.Sum('amount'))['total'] or 0
        self.remaining_amount = self.original_amount - total_paid
        if self.remaining_amount < 0:
            self.remaining_amount = 0
        self.save()

    @property
    def percent_paid(self):
        if self.original_amount:
            return ((self.original_amount - self.remaining_amount) / self.original_amount) * 100
        return 0
    
        
    @property
    def amount_paid(self):
        return self.original_amount - self.remaining_amount


class Rappel(models.Model):
    debt = models.ForeignKey(Debt, on_delete=models.CASCADE)
    date_rappel = models.DateTimeField()
    actif = models.BooleanField(default=True)
    envoye = models.BooleanField(default=False)

    def __str__(self):
        from datetime import date
        today = date.today()
        if self.debt.due_date:
            days_left = (self.debt.due_date - today).days
            if days_left == 0:
                return f"Rappel: {self.debt.title} — C'est l'échéance aujourd'hui!"
            elif days_left == 1:
                return f"Rappel: {self.debt.title} — Il reste 1 jour avant l'échéance"
            else:
                return f"Rappel: {self.debt.title} — Il reste {days_left} jours avant l'échéance"
        return f"Rappel pour {self.debt}"


class Payment(models.Model):
    debt = models.ForeignKey(Debt, related_name='payments', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField(default=timezone.now)
    note = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.amount} on {self.date}"
