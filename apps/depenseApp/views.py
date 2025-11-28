from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Sum
from .models import Depense
from .forms import DepenseForm

from web_project import TemplateLayout

class DepenseListView(ListView):
    model = Depense
    template_name = 'depenseApp/depense_list.html'
    context_object_name = 'depenses'
    
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs)) 
        # Calculer le total des dépenses
        total = Depense.objects.aggregate(Sum('amount'))['amount__sum'] or 0
        context['total_depenses'] = total
        return context


class DepenseDetailView(DetailView):
    model = Depense
    template_name = 'depenseApp/depense_detail.html'
    context_object_name = 'depense'
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs)) 
        return context


class DepenseCreateView(CreateView):
    model = Depense
    form_class = DepenseForm
    template_name = 'depenseApp/depense_form.html'
    success_url = reverse_lazy('depense_list')
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs)) 
        return context

class DepenseUpdateView(UpdateView):
    model = Depense
    form_class = DepenseForm
    template_name = 'depenseApp/depense_form.html'
    success_url = reverse_lazy('depense_list')
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs)) 
        return context


class DepenseDeleteView(DeleteView):
    model = Depense
    template_name = 'depenseApp/depense_confirm_delete.html'
    context_object_name = 'depense'
    success_url = reverse_lazy('depense_list')
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs)) 
        return context
