from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from .models import Rappel

@shared_task
def envoyer_rappels():
    maintenant = timezone.now()
    rappels = Rappel.objects.filter(actif=True, envoye=False, date_rappel__lte=maintenant)
    for rappel in rappels:
        sujet = f"Rappel de paiement pour votre dette"
        message = f"Bonjour {rappel.debt.utilisateur.username},\n\nVotre paiement de {rappel.debt.remaining_amount}€ est bientôt dû le {rappel.debt.due_date}."
        send_mail(
            sujet,
            message,
            'noreply@votreapp.com',
            [rappel.debt.utilisateur.email],
            fail_silently=False,
        )
        rappel.envoye = True
        rappel.save()
        
