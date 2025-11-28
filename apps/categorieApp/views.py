from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.db.models import Q
from .models import Categorie
from .forms import CategorieForm


def page_accueil(request):
    """Page d'accueil avec choix de connexion"""
    if request.user.is_authenticated:
        return redirect('categorieApp:liste_categories')
    return render(request, 'categorieApp/accueil.html')


def connexion_admin(request):
    """Connexion pour les administrateurs"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_staff:
                login(request, user)
                messages.success(request, f"Bienvenue Admin {user.username} !")
                return redirect('categorieApp:liste_categories')
            else:
                messages.error(request, "Vous n'avez pas les droits administrateur.")
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    
    return render(request, 'categorieApp/connexion_admin.html')


def connexion_utilisateur(request):
    """Connexion pour les utilisateurs normaux"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f"Bienvenue {user.username} !")
            return redirect('categorieApp:liste_categories')
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    
    return render(request, 'categorieApp/connexion_utilisateur.html')


def deconnexion(request):
    """Déconnexion de l'utilisateur"""
    logout(request)
    messages.success(request, "Vous avez été déconnecté avec succès.")
    return redirect('categorieApp:accueil')


def est_admin(user):
    """Vérifie si l'utilisateur est administrateur"""
    return user.is_staff


@login_required
def liste_categories(request):
    """
    US 8.5: Consulter les catégories globales et celles créées par l'utilisateur
    """
    if request.user.is_staff:
        # Admin voit toutes les catégories
        categories = Categorie.objects.all()
    else:
        # Utilisateur voit les catégories globales + les siennes
        categories = Categorie.objects.filter(
            Q(est_globale=True) | Q(utilisateur=request.user)
        )
    
    context = {
        'categories': categories,
        'categories_globales': categories.filter(est_globale=True),
        'mes_categories': categories.filter(utilisateur=request.user),
    }
    return render(request, 'categorieApp/liste_categories.html', context)


@login_required
def ajouter_categorie(request):
    """
    US 8.1: Admin ajoute une catégorie globale
    US 8.4: Utilisateur ajoute sa propre catégorie personnalisée
    """
    if request.method == 'POST':
        form = CategorieForm(request.POST, user=request.user)
        if form.is_valid():
            categorie = form.save(commit=False)
            
            # Vérifier que seuls les admins peuvent créer des catégories globales
            if categorie.est_globale and not request.user.is_staff:
                messages.error(request, "Seuls les administrateurs peuvent créer des catégories globales.")
                return redirect('categorieApp:liste_categories')
            
            # Si ce n'est pas une catégorie globale, l'associer à l'utilisateur
            if not categorie.est_globale:
                categorie.utilisateur = request.user
            else:
                categorie.utilisateur = None
            
            categorie.save()
            messages.success(request, "Catégorie ajoutée avec succès!")
            return redirect('categorieApp:liste_categories')
    else:
        form = CategorieForm(user=request.user)
    
    context = {
        'form': form,
        'titre': 'Ajouter une catégorie',
        'bouton': 'Ajouter'
    }
    return render(request, 'categorieApp/form_categorie.html', context)


@login_required
def modifier_categorie(request, pk):
    """
    US 8.2: Admin modifie une catégorie globale existante
    Utilisateur modifie sa catégorie personnelle
    """
    categorie = get_object_or_404(Categorie, pk=pk)
    
    # Vérifier les permissions
    if not categorie.peut_etre_modifiee_par(request.user):
        messages.error(request, "Vous n'avez pas la permission de modifier cette catégorie.")
        return redirect('categorieApp:liste_categories')
    
    if request.method == 'POST':
        form = CategorieForm(request.POST, instance=categorie, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Catégorie modifiée avec succès!")
            return redirect('categorieApp:liste_categories')
    else:
        form = CategorieForm(instance=categorie, user=request.user)
    
    context = {
        'form': form,
        'categorie': categorie,
        'titre': 'Modifier la catégorie',
        'bouton': 'Modifier'
    }
    return render(request, 'categorieApp/form_categorie.html', context)


@login_required
def supprimer_categorie(request, pk):
    """
    US 8.3: Admin supprime une catégorie globale
    US 8.6: Utilisateur supprime uniquement les catégories qu'il a créées
    """
    categorie = get_object_or_404(Categorie, pk=pk)
    
    # Vérifier les permissions
    if not categorie.peut_etre_supprimee_par(request.user):
        messages.error(request, "Vous n'avez pas la permission de supprimer cette catégorie.")
        return redirect('categorieApp:liste_categories')
    
    if request.method == 'POST':
        nom_categorie = categorie.nom
        categorie.delete()
        messages.success(request, f"La catégorie '{nom_categorie}' a été supprimée avec succès!")
        return redirect('categorieApp:liste_categories')
    
    context = {'categorie': categorie}
    return render(request, 'categorieApp/confirmer_suppression.html', context)


@login_required
def detail_categorie(request, pk):
    """Affiche les détails d'une catégorie"""
    categorie = get_object_or_404(Categorie, pk=pk)
    
    # Vérifier que l'utilisateur peut voir cette catégorie
    if not request.user.is_staff and not categorie.est_globale and categorie.utilisateur != request.user:
        messages.error(request, "Vous n'avez pas accès à cette catégorie.")
        return redirect('categorieApp:liste_categories')
    
    context = {'categorie': categorie}
    return render(request, 'categorieApp/detail_categorie.html', context)


@user_passes_test(est_admin)
def categories_par_utilisateur(request):
    """
    US 8.7: Admin voit quelles catégories ont été créées par quel utilisateur
    """
    categories = Categorie.objects.filter(utilisateur__isnull=False).select_related('utilisateur').order_by('utilisateur__username', '-date_creation')
    
    # Grouper par utilisateur
    from collections import defaultdict
    categories_par_user = defaultdict(list)
    
    for cat in categories:
        categories_par_user[cat.utilisateur].append(cat)
    
    context = {
        'categories_par_user': dict(categories_par_user),
        'total_categories': categories.count(),
        'nombre_utilisateurs': len(categories_par_user)
    }
    return render(request, 'categorieApp/categories_par_utilisateur.html', context)


@login_required
def mes_categories(request):
    """Affiche uniquement les catégories créées par l'utilisateur connecté"""
    categories = Categorie.objects.filter(utilisateur=request.user)
    
    context = {
        'categories': categories,
        'titre': 'Mes catégories personnelles'
    }
    return render(request, 'categorieApp/mes_categories.html', context)


@login_required
def categories_globales(request):
    """Affiche uniquement les catégories globales"""
    categories = Categorie.objects.filter(est_globale=True)
    
    context = {
        'categories': categories,
        'titre': 'Catégories globales'
    }
    return render(request, 'categorieApp/categories_globales.html', context)