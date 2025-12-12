from datetime import date, timedelta

from apps.notificationApp.models import Notification
from apps.objectifsEpargnesApp.models import ObjEpargne
# from apps.detteApp.models import Debt   # uncomment and adapt when you have a Debt model


def create_due_soon_epargne_notifications(user):
    """
    Create notifications for saving goals (ObjEpargne) with due date in 2 days.
    This is called when user visits the dashboard, not by cron.
    """
    print("🔍 create_due_soon_epargne_notifications called for user id =", user.id)
    today = date.today()
    due_date = today + timedelta(days=7)

    objectifs = ObjEpargne.objects.filter(user=user, target_date__lte=due_date,target_date__gte=today)
    print("➡️ User",user.id, "has", objectifs.count(), "objectifs")
    print("   ➡️ Objectifs names:", [obj.name for obj in objectifs])
    for obj in objectifs:
         # Compute the link ONCE for this objectif
        link = obj.get_absolute_url() if hasattr(obj, "get_absolute_url") else "/objectifs_epargne/"
        # Avoid duplicate notifications for the same object & day
        already_exists = Notification.objects.filter(
            user=user,
            notification_type="saving_due_soon",
            link=link,
            created_at__date=today,
        ).exists()
        print("   ➡️ Checking objectif id =", obj.goal_id, "already_exists =", already_exists)  
        if not already_exists:
            Notification.objects.create(
                user=user,
                title="Objectif d'épargne bientôt à échéance",
                message=f"Votre objectif « {getattr(obj, 'name', 'Objectif')} » arrive à échéance bientôt.",
                notification_type="saving_due_soon",
                link=obj.get_absolute_url() if hasattr(obj, "get_absolute_url") else "http://127.0.0.1:8000/objectifs_epargne/",
            )
