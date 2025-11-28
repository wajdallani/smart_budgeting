from django.urls import path
from . import views

app_name = 'categorieApp'

urlpatterns = [
    # Accueil et authentification
    path('', views.page_accueil, name='accueil'),
    path('connexion-admin/', views.connexion_admin, name='connexion_admin'),
    path('connexion-utilisateur/', views.connexion_utilisateur, name='connexion_utilisateur'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    
    # Liste et consultation
    path('categories/', views.liste_categories, name='liste_categories'),
    path('detail/<int:pk>/', views.detail_categorie, name='detail_categorie'),
    path('mes-categories/', views.mes_categories, name='mes_categories'),
    path('globales/', views.categories_globales, name='categories_globales'),
    
    # CRUD
    path('ajouter/', views.ajouter_categorie, name='ajouter_categorie'),
    path('modifier/<int:pk>/', views.modifier_categorie, name='modifier_categorie'),
    path('supprimer/<int:pk>/', views.supprimer_categorie, name='supprimer_categorie'),
    
    # Admin
    path('par-utilisateur/', views.categories_par_utilisateur, name='categories_par_utilisateur'),
]