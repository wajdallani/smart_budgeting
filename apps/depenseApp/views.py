# apps/depenseApp/views.py
from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Sum
from django.contrib import messages
from django.contrib.messages import get_messages 

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator

from decimal import Decimal
import datetime

from apps.revenueApp.models import Revenue
from .models import Depense
from .forms import DepenseForm
from .utils import extract_invoice_data_from_file
from web_project import TemplateLayout
from django.contrib.auth.mixins import LoginRequiredMixin

from django.shortcuts import redirect



class DepenseListView(ListView):
    model = Depense
    template_name = 'depenseApp/depense_list.html'
    context_object_name = 'depenses'
    
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        storage = messages.get_messages(self.request)
        for _ in storage:
                pass 
        today = datetime.date.today()
        year, month = today.year, today.month

        context["current_month"] = month
        context["current_year"] = year

        context['total_depenses'] = (
            Depense.objects.aggregate(Sum('amount'))['amount__sum'] or 0
        )

        if not self.request.user.is_authenticated:
            return context

        total_expenses_month = (
            Depense.objects.filter(date__year=year, date__month=month)
            .aggregate(total=Sum("amount"))["total"] or Decimal("0")
        )
        total_revenue_month = (
            Revenue.objects.filter(user=self.request.user, date__year=year, date__month=month)
            .aggregate(total=Sum("amount"))["total"] or Decimal("0")
        )

        revenue_percent = None
        alert_level = None
        alert_message = None

        if total_revenue_month > 0:
            revenue_percent = float(total_expenses_month / total_revenue_month * 100)
            if revenue_percent >= 100:
                alert_level = "danger"
                alert_message = (
                    f"Vos dépenses dépassent vos revenus ({total_expenses_month:.2f} € / {total_revenue_month:.2f} €)."
                )
            elif revenue_percent >= 80:
                alert_level = "warning"
                alert_message = f"Vous avez utilisé {revenue_percent:.0f}% de vos revenus."
            else:
                alert_level = "info"
                alert_message = f"Vous avez utilisé {revenue_percent:.0f}% de vos revenus."
        elif total_revenue_month == 0 and total_expenses_month > 0:
            alert_level = "warning"
            alert_message = "Vous avez des dépenses mais aucun revenu ce mois-ci."

        context.update({
            "total_expenses_month": total_expenses_month,
            "total_revenue_month": total_revenue_month,
            "revenue_percent": revenue_percent,
            "revenue_alert_level": alert_level,
            "revenue_alert_message": alert_message,
        })

        return context


class DepenseDetailView(DetailView):
    model = Depense
    template_name = 'depenseApp/depense_detail.html'
    context_object_name = 'depense'

    def get_context_data(self, **kwargs):
        return TemplateLayout.init(self, super().get_context_data(**kwargs))


class DepenseCreateView(LoginRequiredMixin, CreateView):
    model = Depense
    form_class = DepenseForm
    template_name = 'depenseApp/depense_form.html'
    success_url = reverse_lazy('depense_list')

    def get(self, request, *args, **kwargs):
        # On consomme tous les messages restants (par ex. "Dépense créée avec succès.")
        list(get_messages(request))
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        return TemplateLayout.init(self, super().get_context_data(**kwargs))

    def form_valid(self, form):
        self.object = form.save(commit=False)

        # if hasattr(self.object, "user") and self.request.user.is_authenticated:
        #     self.object.user = self.request.user
        self.object.user = self.request.user
        if not self.object.amount:
            form.add_error("amount", "Montant obligatoire.")
        if not self.object.date:
            form.add_error("date", "Date obligatoire.")

        if form.errors:
            return self.form_invalid(form)

        self.object.save()
        form.save_m2m()
        messages.success(self.request, "Dépense créée avec succès.")
        # return super().form_valid(form)
        return redirect(self.get_success_url())
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class DepenseUpdateView(UpdateView):
    model = Depense
    form_class = DepenseForm
    template_name = 'depenseApp/depense_form.html'
    success_url = reverse_lazy('depense_list')

    def get_context_data(self, **kwargs):
        return TemplateLayout.init(self, super().get_context_data(**kwargs))
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class DepenseDeleteView(DeleteView):
    model = Depense
    template_name = 'depenseApp/depense_confirm_delete.html'
    context_object_name = 'depense'
    success_url = reverse_lazy('depense_list')

    def get_context_data(self, **kwargs):
        return TemplateLayout.init(self, super().get_context_data(**kwargs))


@require_POST
def depense_ocr_api(request):
    """
    API AJAX:
    - reçoit une image 'facture_img'
    - retourne {amount, date} en JSON
    """
    file = request.FILES.get("facture_img")
    if not file:
        return JsonResponse({"error": "Aucun fichier reçu."}, status=400)

    data = extract_invoice_data_from_file(file) or {}
    # data = { "amount": "...", "date": "YYYY-MM-DD" }

    return JsonResponse(data)

