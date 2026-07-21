from django import forms
from .models import Income

class IncomeForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))

    class Meta:
        model = Income
        fields = ['title', 'amount', 'source', 'date', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Monthly Salary'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'source': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional notes...'}),
        }
