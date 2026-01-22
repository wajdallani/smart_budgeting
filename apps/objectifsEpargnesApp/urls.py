from django.urls import path
from . import views

urlpatterns = [
    path('', views.ObjectifEpargneListView.as_view(), name='listEpargne'),
    path('create/', views.ObjectifEpargneCreateView.as_view(), name='createEpargne'),
    path('<int:pk>/', views.ObjectifEpargneDetailView.as_view(), name='detailEpargne'),
    path('<int:pk>/edit/', views.ObjectifEpargneUpdateView.as_view(), name='editEpargne'),
    path('<int:pk>/delete/', views.ObjectifEpargneDeleteView.as_view(), name='deleteEpargne'),
    path('<int:pk>/contributions/add/', views.ObjEpargneContributionCreateView.as_view(), name='addContribution'),
    path('<int:pk>/contributions/<int:cont_id>/edit/', views.ObjEpargneContributionUpdateView.as_view(), name='editContribution'),
    path('<int:pk>/contributions/<int:cont_id>/delete/', views.ObjEpargneContributionDeleteView.as_view(), name='deleteContribution'),
]