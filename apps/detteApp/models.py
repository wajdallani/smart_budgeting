# detteApp/models.py
from django.db import models
from django.urls import reverse
from django.utils import timezone

# Create your models here.

class Debt(models.Model):
    # Qui doit à qui : fields adaptables selon besoins
    title = models.CharField(max_length=200)  # ex: "Prêt à Paul"
    creditor = models.CharField(max_length=150, blank=True)  # qui prête
    debtor = models.CharField(max_length=150, blank=True)    # qui doit
    original_amount = models.DecimalField(max_digits=12, decimal_places=2)
    remaining_amount = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # %
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
        # recalculer remaining à partir des paiements
        total_paid = self.payments.aggregate(total=models.Sum('amount'))['total'] or 0
        self.remaining_amount = self.original_amount - total_paid
        # clamp à zéro
        if self.remaining_amount < 0:
            self.remaining_amount = 0
        self.save()
    
    def percent_paid(self):
        if self.original_amount:
            return ((self.original_amount - self.remaining_amount) / self.original_amount) * 100
        return 0

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

