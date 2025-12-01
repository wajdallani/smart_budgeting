from django import forms
from .models import Categorie


class CategorieForm(forms.ModelForm):
    class Meta:
        model = Categorie
        fields = ['nom', 'description', 'est_globale']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom de la catégorie',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description (optionnel)'
            }),
            'est_globale': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'nom': 'Nom de la catégorie',
            'description': 'Description',
            'est_globale': 'Catégorie globale (accessible à tous)'
        }
        help_texts = {
            'nom': 'Choisissez un nom unique pour votre catégorie',
            'est_globale': 'Cochez cette case pour rendre la catégorie accessible à tous les utilisateurs (admin uniquement)'
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Cacher le champ est_globale pour les utilisateurs non-admin
        if self.user and not self.user.is_staff:
            self.fields['est_globale'].widget = forms.HiddenInput()
            self.fields['est_globale'].initial = False
        
        # Rendre la description optionnelle
        self.fields['description'].required = False
    
    def clean_nom(self):
        """Valider que le nom n'est pas vide et n'existe pas déjà pour cet utilisateur"""
        nom = self.cleaned_data.get('nom')
        
        if not nom or nom.strip() == '':
            raise forms.ValidationError("Le nom de la catégorie ne peut pas être vide.")
        
        # Vérifier les doublons pour l'utilisateur
        if self.user and not self.cleaned_data.get('est_globale', False):
            existing = Categorie.objects.filter(
                nom__iexact=nom,
                utilisateur=self.user
            )
            
            # Si on modifie, exclure la catégorie actuelle
            if self.instance and self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise forms.ValidationError(f"Vous avez déjà une catégorie nommée '{nom}'.")
        
        return nom.strip()
    
    def clean_est_globale(self):
        """Vérifier que seuls les admins peuvent créer des catégories globales"""
        est_globale = self.cleaned_data.get('est_globale', False)
        
        if est_globale and self.user and not self.user.is_staff:
            raise forms.ValidationError("Seuls les administrateurs peuvent créer des catégories globales.")
        
        return est_globale