
# Create your views here.

# Create your views here.
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import ObjEpargne
from .forms import ObjEpargneForm
from web_project import TemplateLayout
from apps.notificationApp.views import create_obj_epargne_reminder
from django.shortcuts import get_object_or_404
from django.urls import reverse
from .models import ObjEpargne, ObjEpargneContribution
from .forms import ObjEpargneForm, ObjEpargneContributionForm
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import UpdateView, DeleteView
from .models import ObjEpargne, ObjEpargneContribution
from .forms import ObjEpargneContributionForm
#READ
class ObjectifEpargneListView( ListView):
    model = ObjEpargne
    template_name = 'objectifs_list.html'
    context_object_name = 'objectifs'

    def get_queryset(self):
        return ObjEpargne.objects.filter(user=self.request.user)
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
    


class ObjEpargneContributionCreateView(LoginRequiredMixin, CreateView):
    model = ObjEpargneContribution
    form_class = ObjEpargneContributionForm
    template_name = "contribution_form_create.html"

    def dispatch(self, request, *args, **kwargs):
        # Ensure the goal exists AND belongs to the logged-in user
        self.goal = get_object_or_404(ObjEpargne, pk=kwargs["pk"], user=request.user)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.goal = self.goal
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("detailEpargne", kwargs={"pk": self.goal.pk})

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context["objectif"] = self.goal
        return context

class ObjEpargneContributionUpdateView(LoginRequiredMixin, UpdateView):
    model = ObjEpargneContribution
    form_class = ObjEpargneContributionForm
    template_name = "contribution_form_update.html"
    login_url = "/auth/login/"

    def dispatch(self, request, *args, **kwargs):
        # Ensure goal belongs to user
        self.goal = get_object_or_404(ObjEpargne, pk=kwargs["pk"], user=request.user)
        # Ensure contribution belongs to this goal
        self.contribution = get_object_or_404(ObjEpargneContribution, pk=kwargs["cont_id"], goal=self.goal)
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self.contribution

    def get_success_url(self):
        return reverse("detailEpargne", kwargs={"pk": self.goal.pk})

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context["objectif"] = self.goal
        return context


class ObjEpargneContributionDeleteView(LoginRequiredMixin, DeleteView):
    model = ObjEpargneContribution
    template_name = "contribution_confirm_delete.html"
    login_url = "/auth/login/"

    def dispatch(self, request, *args, **kwargs):
        self.goal = get_object_or_404(ObjEpargne, pk=kwargs["pk"], user=request.user)
        self.contribution = get_object_or_404(ObjEpargneContribution, pk=kwargs["cont_id"], goal=self.goal)
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self.contribution

    def get_success_url(self):
        return reverse("detailEpargne", kwargs={"pk": self.goal.pk})

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context["objectif"] = self.goal
        return context
