from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import datetime, time

from .models import Debt, Rappel


@receiver(post_save, sender=Debt)
def create_rappel_for_due_date(sender, instance: Debt, created, **kwargs):
    """Create a Rappel when a Debt with a due_date is saved and no rappel exists.

    - If `due_date` is set, and there is no Rappel for this debt with the same
      date, create one (actif=True, envoye=False).
    - Reminder is created immediately so it appears in notifications right away.
    - This avoids duplicating reminders when editing a debt multiple times.
    """
    if not instance.due_date:
        return

    maintenant = timezone.now()
    # check existing reminders for this debt with same date (date part)
    existing = Rappel.objects.filter(debt=instance, date_rappel__date=instance.due_date)
    if existing.exists():
        return

    # Create reminder immediately (now) so it appears in notifications right away
    # The __str__ method will calculate remaining days dynamically
    rappel_dt = maintenant

    Rappel.objects.create(debt=instance, date_rappel=rappel_dt, actif=True, envoye=False)
