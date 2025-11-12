
# Create your views here.
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import ObjEpargne
from .forms import ObjectifEpargneForm
#READ
class ObjectifEpargneListView(LoginRequiredMixin, ListView):
    model = ObjEpargne
    template_name = 'epargne/objectifs_list.html'
    context_object_name = 'objectifs'

    def get_queryset(self):
        return ObjEpargne.objects.filter(user=self.request.user)
#Read details
class ObjectifEpargneDetailView(LoginRequiredMixin, DetailView):
    model = ObjEpargne
    template_name = 'epargne/objectif_detail.html'
    context_object_name = 'objectif'

    def get_queryset(self):
        return ObjEpargne.objects.filter(user=self.request.user)
#create
class ObjectifEpargneCreateView(LoginRequiredMixin, CreateView):
    model = ObjEpargne
    form_class = ObjectifEpargneForm
    template_name = 'epargne/objectif_form.html'
    success_url = reverse_lazy('epargne:list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
#update
class ObjectifEpargneUpdateView(LoginRequiredMixin, UpdateView):
    model = ObjEpargne
    form_class = ObjectifEpargneForm
    template_name = 'epargne/objectif_form.html'
    success_url = reverse_lazy('epargne:list')

    def get_queryset(self):
        return ObjEpargne.objects.filter(user=self.request.user)
#delete
class ObjectifEpargneDeleteView(LoginRequiredMixin, DeleteView):
    model = ObjEpargne
    template_name = 'epargne/objectif_confirm_delete.html'
    success_url = reverse_lazy('epargne:list')

    def get_queryset(self):
        return ObjEpargne.objects.filter(user=self.request.user)
