from django import forms
from .models import Debt, Payment

class DebtForm(forms.ModelForm):
    class Meta:
        model = Debt
        fields = ['title', 'creditor', 'debtor', 'original_amount', 'remaining_amount',
                  'interest_rate', 'due_date', 'description']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        } 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'due_date':  # skip due_date because it's already styled
                field.widget.attrs.update({'class': 'form-control'})

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'date', 'note']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
               if field_name != 'date':  # skip date because it's already styled
                field.widget.attrs.update({'class': 'form-control'})