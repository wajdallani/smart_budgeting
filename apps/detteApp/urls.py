# detteApp/urls.py
from django.urls import path
from . import views

app_name = 'detteApp'

urlpatterns = [
    path('', views.DebtListView.as_view(), name='debt_list'),
    path('debt/add/', views.DebtCreateView.as_view(), name='debt_add'),
    path('debt/<int:pk>/', views.DebtDetailView.as_view(), name='debt_detail'),
    path('debt/<int:pk>/edit/', views.DebtUpdateView.as_view(), name='debt_edit'),
    path('debt/<int:pk>/delete/', views.DebtDeleteView.as_view(), name='debt_delete'),
    path('debt/<int:pk>/add-payment/', views.AddPaymentView.as_view(), name='add_payment'),
    path('rappels/', views.liste_rappels, name='liste_rappels'),
    path('rappels/ajouter/', views.ajouter_rappel, name='ajouter_rappel'),
    path('rappels/mark-seen/', views.mark_rappel_seen, name='mark_rappel_seen'),
    
]