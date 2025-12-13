# apps/groupApp/urls.py
from django.urls import path
from . import views

app_name = 'groupApp'

urlpatterns = [
    path('', views.group_list, name='group_list'),
    path('create/', views.group_create, name='group_create'),
    path('<int:pk>/edit/', views.group_update, name='group_update'),
    path('<int:pk>/delete/', views.group_delete, name='group_delete'),
]