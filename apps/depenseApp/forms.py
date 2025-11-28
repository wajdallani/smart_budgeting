from django import forms
from .models import Depense


class DepenseForm(forms.ModelForm):
    class Meta:
        model = Depense
        fields = ["amount", "date", "notes", "facture_img"]  # ← Enlevez depense_id
        widgets = {
            "amount": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "0.00", "step": "0.01"}
            ),
            "date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"},
                format='%Y-%m-%d'
            ),
            "notes": forms.Textarea(
                attrs={"rows": 4, "class": "form-control", "placeholder": "Notes sur cette dépense..."}
            ),
            "facture_img": forms.FileInput(
                attrs={"class": "form-control"}
            ),
        }
        labels = {
            "amount": "Montant (€)",
            "date": "Date",
            "notes": "Notes",
            "facture_img": "Facture (Image)",
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Activer le format de date pour l'input HTML5
        self.fields['date'].input_formats = ['%Y-%m-%d']