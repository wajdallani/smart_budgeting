from django.contrib import admin
from .models import Categorie


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ['nom', 'est_globale', 'utilisateur', 'date_creation', 'date_modification']
    list_filter = ['est_globale', 'date_creation']
    search_fields = ['nom', 'description', 'utilisateur__username']
    readonly_fields = ['date_creation', 'date_modification']
    list_per_page = 20
    
    fieldsets = (
        ('Informations principales', {
            'fields': ('nom', 'description', 'est_globale')
        }),
        ('Association utilisateur', {
            'fields': ('utilisateur',),
            'description': 'Laisser vide pour les catégories globales'
        }),
        ('Dates', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs

    def save_model(self, request, obj, form, change):
        # Si c'est une catégorie globale, pas d'utilisateur associé
        if obj.est_globale:
            obj.utilisateur = None
        super().save_model(request, obj, form, change)
    
    actions = ['rendre_globale', 'rendre_personnelle']
    
    def rendre_globale(self, request, queryset):
        """Action pour rendre des catégories globales"""
        updated = queryset.update(est_globale=True, utilisateur=None)
        self.message_user(request, f"{updated} catégorie(s) rendue(s) globale(s).")
    rendre_globale.short_description = "Rendre les catégories sélectionnées globales"
    
    def rendre_personnelle(self, request, queryset):
        """Action pour rendre des catégories personnelles"""
        updated = queryset.update(est_globale=False)
        self.message_user(request, f"{updated} catégorie(s) rendue(s) personnelle(s).")
    rendre_personnelle.short_description = "Rendre les catégories sélectionnées personnelles"