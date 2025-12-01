from django.shortcuts import render

# Create your views here.
# gestion_dettes/views.py
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.db import transaction
from .models import Debt, Payment
from .forms import DebtForm, PaymentForm
from web_project import TemplateLayout

class DebtListView(ListView):
    model = Debt
    template_name = 'detteApp/debt_list.html'
    context_object_name = 'debts'

    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        return context

class DebtDetailView(DetailView):
    model = Debt
    template_name = 'detteApp/debt_detail.html'
    context_object_name = 'debt'

    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        return context


class DebtCreateView(CreateView):
    model = Debt
    form_class = DebtForm
    template_name = 'detteApp/debt_form_create.html'

    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        return context


    def form_valid(self, form):
        # s'assurer que remaining_amount est initialisé
        debt = form.save(commit=False)
        if not debt.remaining_amount:
            debt.remaining_amount = debt.original_amount
        debt.save()
        return super().form_valid(form)

class DebtUpdateView(UpdateView):
    model = Debt
    form_class = DebtForm
    template_name = 'detteApp/debt_form_update.html'

    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        return context


class DebtDeleteView(DeleteView):
    model = Debt
    template_name = 'detteApp/debt_confirm_delete.html'
    success_url = reverse_lazy('detteApp:debt_list')
    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        return context


# Vue pour ajouter un paiement à une dette existante
class AddPaymentView(CreateView):
    model = Payment
    form_class = PaymentForm
    template_name = 'detteApp/add_payment.html'

    def dispatch(self, request, *args, **kwargs):
        self.debt = get_object_or_404(Debt, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        payment = form.save(commit=False)
        payment.debt = self.debt

        # transactionnel : enregistrer le paiement et mettre à jour la dette
        with transaction.atomic():
            payment.save()
            # recalculer remaining à partir des paiements (robuste)
            self.debt.update_remaining()

        return redirect(self.debt.get_absolute_url())

    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        return context
