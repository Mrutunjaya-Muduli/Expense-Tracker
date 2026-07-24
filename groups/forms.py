from django import forms
from django.contrib.auth.models import User
from .models import GroupExpense, Group

class GroupExpenseForm(forms.ModelForm):
    split_with = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Split equally with"
    )

    class Meta:
        model = GroupExpense
        fields = ['title', 'amount', 'date', 'paid_by', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        group = kwargs.pop('group', None)
        super().__init__(*args, **kwargs)
        if group:
            self.fields['paid_by'].queryset = group.members.all()
            self.fields['split_with'].queryset = group.members.all()
            # Default paid_by to None so they have to choose, or view can prefill
            # Set initial for split_with to all members
            self.fields['split_with'].initial = group.members.all()
