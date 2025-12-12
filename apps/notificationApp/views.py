from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.views import View
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Notification
from web_project import TemplateLayout
from datetime import date, timedelta
from apps.objectifsEpargnesApp.models import ObjEpargne


def create_obj_epargne_reminder(user, obj_epargne, days_left=None):
    """
    Crée une notification de rappel pour un objectif d'épargne.
    À appeler depuis objectifsEpargnesApp (ex: vue detail, cron, etc.).
    """
    title = "Rappel objectif d'épargne"
    message_parts = []

    if hasattr(obj_epargne, "nom"):
        base_text = f"Votre objectif « {obj_epargne.nom} » approche."
    else:
        base_text = "Votre objectif d'épargne approche."

    message_parts.append(base_text)

    if days_left is not None:
        message_parts.append(f"Il reste {days_left} jours pour l’atteindre.")

    message_parts.append("Continuez, vous êtes sur la bonne voie 💪.")

    message = " ".join(message_parts)

    Notification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type="saving_reminder",  # type = rappel objectif épargne
        link=obj_epargne.get_absolute_url() if hasattr(obj_epargne, "get_absolute_url") else "",
    )


def create_debt_reminder(user, debt, amount_left=None, due_date=None):
    """
    Crée une notification de rappel pour une dette.
    À appeler depuis l'app de dettes (vue détail, échéance, etc.).
    """
    title = "Rappel de dette"
    message_parts = []

    if hasattr(debt, "nom"):
        base_text = f"Rappel pour votre dette « {debt.nom} »."
    else:
        base_text = "Rappel pour une de vos dettes."

    message_parts.append(base_text)

    if amount_left is not None:
        message_parts.append(f"Montant restant : {amount_left}.")

    if due_date is not None:
        message_parts.append(f"Échéance : {due_date}.")

    message = " ".join(message_parts)

    Notification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type="debt_reminder",  # type = rappel dette
        link=debt.get_absolute_url() if hasattr(debt, "get_absolute_url") else "",
    )



class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = "notifications_list.html"
    context_object_name = "notifications"

    def get_queryset(self):
        # On filtre par utilisateur connecté
        return Notification.objects.filter(user=self.request.user).order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        return context
class MarkNotificationAsReadView(LoginRequiredMixin, View):

    def post(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, user=request.user)
        notification.is_read = True
        notification.save()

        # Redirection vers la ressource concernée
        if notification.link:
            return HttpResponseRedirect(notification.link)

        return redirect("notifications_list")
    
class MarkAllNotificationsAsReadView(LoginRequiredMixin, View):

    def post(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return redirect("notifications_list")



#test
class TestNotificationView(LoginRequiredMixin, View):

    def get(self, request):
        Notification.objects.create(
            user=request.user,
            title="Hello Test!",
            message="This notification was created from TestNotificationView.",
            notification_type="test",
        )
        return redirect('/')