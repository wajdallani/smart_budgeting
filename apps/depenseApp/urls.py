from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('', RedirectView.as_view(url='list/', permanent=False)),
    path('list/', views.DepenseListView.as_view(), name='depense_list'),
    path('detail/<int:pk>/', views.DepenseDetailView.as_view(), name='depense_detail'),
    path('create/', views.DepenseCreateView.as_view(), name='depense_create'),
    path('update/<int:pk>/', views.DepenseUpdateView.as_view(), name='depense_update'),
    path('delete/<int:pk>/', views.DepenseDeleteView.as_view(), name='depense_delete'),
    path('ocr-invoice/', views.depense_ocr_api, name='depense_ocr'),
]