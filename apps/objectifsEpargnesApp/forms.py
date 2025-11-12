from django import forms
from .models import ObjectifEpargne

class ObjectifEpargneForm(forms.ModelForm):
    class Meta:
        model = ObjectifEpargne
        fields = [
            'titre',
            'description',
            'montant_cible',
            'date_limite',
            'priorite',
        ]
