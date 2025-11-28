from django.urls import path
from . import views

urlpatterns = [
    path('', views.revenue_list, name='revenue_list'),
    path('ajouter/', views.revenue_create, name='revenue_create'),
    path('modifier/<int:pk>/', views.revenue_update, name='revenue_update'),
    path('supprimer/<int:pk>/', views.revenue_delete, name='revenue_delete'),
]
