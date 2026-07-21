from django import forms
from .models import Expense, Category

class ExpenseForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))

    class Meta:
        model = Expense
        fields = ['title', 'amount', 'category', 'payment_method', 'date', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Grocery Shopping'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional notes...'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Show categories created by user OR default global categories (user is None)
            self.fields['category'].queryset = Category.objects.filter(models.Q(user=user) | models.Q(user__isnull=True))

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name', 'icon', 'color']
        widgets = {
            'category_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category Name'}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. bi-tag (Bootstrap Icon class)'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
        }
