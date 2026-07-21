import datetime
from django.test import TestCase
from django.contrib.auth.models import User
from .models import Category, Expense
from income.models import Income
from budget.models import Budget

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
