
# Create your views here.

# Create your views here.
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import ObjEpargne
from .forms import ObjEpargneForm
from web_project import TemplateLayout
from apps.notificationApp.views import create_obj_epargne_reminder

#READ
class ObjectifEpargneListView( ListView):
    model = ObjEpargne
    template_name = 'objectifs_list.html'
    context_object_name = 'objectifs'

    # def get_queryset(self):
    #     return ObjEpargne.objects.filter(user=self.request.user)
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs)) 
        return context
#Read details
class ObjectifEpargneDetailView( DetailView):
    model = ObjEpargne
    template_name = 'objectif_detail.html'
    context_object_name = 'objectif'

    # def get_queryset(self):
    #     return ObjEpargne.objects.filter(user=self.request.user)
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        objectif = self.get_object()
        context["contributions"] = objectif.contributions.all()
        context["total_contributions"] = objectif.total_contributed
        return context
#create
class ObjectifEpargneCreateView( LoginRequiredMixin,CreateView):
    model = ObjEpargne
    form_class = ObjEpargneForm
    template_name = 'objectif_form_create.html'
    success_url = reverse_lazy('listEpargne')

    def form_valid(self, form):
        print("👉​ DEBUG user:", self.request.user, self.request.user.is_authenticated)
        form.instance.user = self.request.user
        create_obj_epargne_reminder(self.request.user, self.object)

        return super().form_valid(form)
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        return context
#update
class ObjectifEpargneUpdateView( UpdateView):
    model = ObjEpargne
    form_class = ObjEpargneForm
    template_name = 'objectif_form_update.html'
    success_url = reverse_lazy('listEpargne')

    # def get_queryset(self):
    #     return ObjEpargne.objects.filter(user=self.request.user)
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        return context
#delete
class ObjectifEpargneDeleteView( DeleteView):
    model = ObjEpargne
    template_name = 'objectif_confirm_delete.html'
    success_url = reverse_lazy('listEpargne')

    # def get_queryset(self):
    #     return ObjEpargne.objects.filter(user=self.request.user)
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        return context