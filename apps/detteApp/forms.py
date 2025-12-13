from django import forms
from .models import Debt, Payment, Rappel


class DebtForm(forms.ModelForm):
    class Meta:
        model = Debt
        # ⚠️ remaining_amount est volontairement exclu pour éviter une saisie utilisateur
        fields = [
            'title',
            'creditor',
            'debtor',
            'original_amount',
            'interest_rate',
            'due_date',
            'description',
        ]

        widgets = {
            'due_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'date', 'note']

        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class RappelForm(forms.ModelForm):
    class Meta:
        model = Rappel
        fields = ['date_rappel', 'actif']

        widgets = {
            'date_rappel': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),


        }