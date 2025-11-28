from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Revenue(models.Model):
    CATEGORY_CHOICES = [
        ('salary', 'Salaire'),
        ('bonus', 'Prime'),
        ('investment', 'Investissement'),
        ('gift', 'Cadeau'),
        ('other', 'Autre'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='revenues')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True, null=True)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.category} - {self.amount} DT - {self.date}"



class Meta :
        ordering = ['-date']


def __str__self(self) :
        return f" {self.category} - {self.amount} - DT - {self.date}"