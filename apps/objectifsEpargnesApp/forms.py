from django import forms
from .models import ObjEpargne, ObjEpargneContribution

class ObjEpargneForm(forms.ModelForm):
    # Optional: nicer HTML5 picker for the date
    target_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    class Meta:
        model = ObjEpargne
        # Match model fields (no titre/description/etc.)
        fields = ['name', 'target_amount', 'target_date', 'status']
        labels = {
            'name': 'Nom',
            'target_amount': 'Montant cible',
            'target_date': 'Date cible',
            'status': 'Statut',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
class ObjEpargneContributionForm(forms.ModelForm):
    added_at = forms.DateTimeField(
        required=True,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )

    class Meta:
        model = ObjEpargneContribution
        fields = ['amount', 'added_at']
        labels = {'amount': 'Montant', 'added_at': 'Ajouté le'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['amount'].widget.attrs.update({'class': 'form-control'})
        self.fields['added_at'].widget.attrs.update({'class': 'form-control'})
