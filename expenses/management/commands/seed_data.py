import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from expenses.models import Category, Expense
from income.models import Income
from budget.models import Budget
from expenses.utils import ensure_default_categories

class Command(BaseCommand):
    help = 'Seeds initial default categories, demo user, and sample financial data.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Creating default global categories..."))
        categories = ensure_default_categories(user=None)
        
        # Create demo user
        user, created = User.objects.get_or_create(username='demo', defaults={'email': 'demo@example.com', 'first_name': 'John', 'last_name': 'Doe'})
        if created:
            user.set_password('demo1234')
            user.save()
            self.stdout.write(self.style.SUCCESS("Created demo user (username: demo, password: demo1234)"))
        else:
            self.stdout.write(self.style.NOTICE("Demo user already exists."))

        # Ensure user also has access to default categories
        cat_map = {c.category_name: c for c in Category.objects.filter(user__isnull=True)}

        # Current date info
        today = datetime.date.today()
        current_month = today.strftime("%Y-%m")

        # Seed Income
        if not Income.objects.filter(user=user).exists():
            Income.objects.create(
                user=user,
                title='Monthly Salary',
                amount=4500.00,
                source='Salary',
                date=today.replace(day=1),
                description='Primary employment income'
            )
            Income.objects.create(
                user=user,
                title='Freelance Design Project',
                amount=850.00,
                source='Freelance',
                date=today - datetime.timedelta(days=5),
                description='UI/UX contract work'
            )
            self.stdout.write(self.style.SUCCESS("Added sample incomes."))

        # Seed Expenses
        if not Expense.objects.filter(user=user).exists():
            sample_expenses = [
                ('House Rent', 1200.00, 'Rent', 'UPI/Bank Transfer', today.replace(day=2), 'Monthly apartment rent'),
                ('Grocery Shopping', 245.50, 'Food', 'Credit Card', today - datetime.timedelta(days=10), 'Supermarket groceries'),
                ('Electricity & Gas Bill', 135.00, 'Bills', 'Debit Card', today - datetime.timedelta(days=8), 'Utility bill payment'),
                ('Dinner at Italian Restaurant', 85.00, 'Food', 'Credit Card', today - datetime.timedelta(days=4), 'Dining with friends'),
                ('Gasoline refill', 55.00, 'Transport', 'Cash', today - datetime.timedelta(days=3), 'Full tank petrol'),
                ('Netflix & Spotify Subscription', 28.00, 'Entertainment', 'Credit Card', today.replace(day=5), 'Streaming services'),
                ('Pharmacy & Medications', 42.00, 'Medical', 'Debit Card', today - datetime.timedelta(days=6), 'Vitamin supplements'),
            ]
            for title, amt, cat_name, p_method, exp_date, desc in sample_expenses:
                Expense.objects.create(
                    user=user,
                    title=title,
                    amount=amt,
                    category=cat_map.get(cat_name),
                    payment_method=p_method,
                    date=exp_date,
                    description=desc
                )
            self.stdout.write(self.style.SUCCESS("Added sample expenses."))

        # Seed Budget
        if not Budget.objects.filter(user=user, month=current_month, category__isnull=True).exists():
            Budget.objects.create(
                user=user,
                month=current_month,
                total_budget=2500.00
            )
            # Food category budget cap
            if 'Food' in cat_map:
                Budget.objects.create(
                    user=user,
                    month=current_month,
                    total_budget=400.00,
                    category=cat_map['Food']
                )
            self.stdout.write(self.style.SUCCESS("Added sample monthly budgets."))

        self.stdout.write(self.style.SUCCESS("Seed data completed successfully!"))
