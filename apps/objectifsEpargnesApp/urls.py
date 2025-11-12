from django.urls import path
from . import views

urlpatterns = [
    path('', views.ObjectifEpargneListView.as_view(), name='list'),
    path('create/', views.ObjectifEpargneCreateView.as_view(), name='create'),
    path('<int:pk>/', views.ObjectifEpargneDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.ObjectifEpargneUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.ObjectifEpargneDeleteView.as_view(), name='deleteEpargne'),
]