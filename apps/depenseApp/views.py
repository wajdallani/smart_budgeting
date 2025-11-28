from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Sum
from .models import Depense
from .forms import DepenseForm


class DepenseListView(ListView):
    model = Depense
    template_name = 'depenseApp/depense_list.html'
    context_object_name = 'depenses'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Calculer le total des dépenses
        total = Depense.objects.aggregate(Sum('amount'))['amount__sum'] or 0
        context['total_depenses'] = total
        return context


class DepenseDetailView(DetailView):
    model = Depense
    template_name = 'depenseApp/depense_detail.html'
    context_object_name = 'depense'


class DepenseCreateView(CreateView):
    model = Depense
    form_class = DepenseForm
    template_name = 'depenseApp/depense_form.html'
    success_url = reverse_lazy('depense_list')


class DepenseUpdateView(UpdateView):
    model = Depense
    form_class = DepenseForm
    template_name = 'depenseApp/depense_form.html'
    success_url = reverse_lazy('depense_list')


class DepenseDeleteView(DeleteView):
    model = Depense
    template_name = 'depenseApp/depense_confirm_delete.html'
    context_object_name = 'depense'
    success_url = reverse_lazy('depense_list')