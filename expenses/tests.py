import datetime
from django.test import TestCase
from django.contrib.auth.models import User
from .models import Category, Expense
from .forms import ExpenseForm

class ExpenseModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.category = Category.objects.create(category_name='Food', icon='bi-cup', color='#ff0000')

    def test_expense_creation(self):
        exp = Expense.objects.create(
            user=self.user,
            title='Lunch',
            amount=25.50,
            category=self.category,
            payment_method='Cash',
            date=datetime.date.today()
        )
        self.assertEqual(exp.amount, 25.50)
        self.assertEqual(exp.user.username, 'testuser')

    def test_expense_form_initialization(self):
        form = ExpenseForm(user=self.user)
        self.assertIn(self.category, form.fields['category'].queryset)
