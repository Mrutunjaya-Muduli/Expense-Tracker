import datetime
from django import forms
from .models import Budget
from expenses.models import Category

class BudgetForm(forms.ModelForm):
    month = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'month'}),
        initial=datetime.date.today().strftime('%Y-%m'),
        help_text="Select Month and Year"
    )

    class Meta:
        model = Budget
        fields = ['month', 'total_budget', 'category']
        widgets = {
            'total_budget': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['category'].required = False
        self.fields['category'].empty_label = "-- Overall Monthly Budget --"
        if user:
            self.fields['category'].queryset = Category.objects.filter(models.Q(user=user) | models.Q(user__isnull=True))
