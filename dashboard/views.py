import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum
from django.db.models.functions import ExtractMonth, ExtractYear

from income.models import Income
from expenses.models import Expense, Category
from budget.models import Budget

@login_required
def dashboard_view(request):
    user = request.user
    today = datetime.date.today()
    current_month_str = today.strftime('%Y-%m')

    # Total overall metrics
    total_income = Income.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or 0
    total_expense = Expense.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or 0
    current_balance = total_income - total_expense

    # Current month metrics
    monthly_income = Income.objects.filter(user=user, date__year=today.year, date__month=today.month).aggregate(total=Sum('amount'))['total'] or 0
    monthly_expense = Expense.objects.filter(user=user, date__year=today.year, date__month=today.month).aggregate(total=Sum('amount'))['total'] or 0

    monthly_budget_obj = Budget.objects.filter(user=user, month=current_month_str, category__isnull=True).first()
    monthly_budget = monthly_budget_obj.total_budget if monthly_budget_obj else 0
    remaining_budget = monthly_budget - monthly_expense if monthly_budget > 0 else 0
    is_budget_exceeded = monthly_expense > monthly_budget if monthly_budget > 0 else False
    budget_usage_percent = round((monthly_expense / monthly_budget * 100), 1) if monthly_budget > 0 else 0

    # Savings Rate
    savings_rate = round(((total_income - total_expense) / total_income * 100), 1) if total_income > 0 else 0

    # Recent Transactions (Combines Incomes & Expenses)
    recent_expenses = list(Expense.objects.filter(user=user).order_by('-date', '-id')[:5])
    recent_incomes = list(Income.objects.filter(user=user).order_by('-date', '-id')[:5])

    context = {
        'total_income': total_income,
        'total_expense': total_expense,
        'current_balance': current_balance,
        'monthly_income': monthly_income,
        'monthly_expense': monthly_expense,
        'monthly_budget': monthly_budget,
        'remaining_budget': remaining_budget,
        'is_budget_exceeded': is_budget_exceeded,
        'budget_usage_percent': budget_usage_percent,
        'savings_rate': savings_rate,
        'recent_expenses': recent_expenses,
        'recent_incomes': recent_incomes,
    }
    return render(request, 'dashboard/dashboard.html', context)


@login_required
def chart_data_api(request):
    """API endpoint providing JSON structured data for Chart.js charts."""
    user = request.user
    today = datetime.date.today()

    # 1. Income vs Expense summary
    total_inc = Income.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or 0
    total_exp = Expense.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or 0

    # 2. Category-wise Expenses
    cat_expenses = Expense.objects.filter(user=user) \
        .values('category__category_name', 'category__color') \
        .annotate(total=Sum('amount')) \
        .order_by('-total')

    category_labels = []
    category_amounts = []
    category_colors = []

    for item in cat_expenses:
        name = item['category__category_name'] or 'Uncategorized'
        color = item['category__color'] or '#6c757d'
        category_labels.append(name)
        category_amounts.append(float(item['total']))
        category_colors.append(color)

    # 3. Monthly Trends (Last 6 Months)
    months_labels = []
    monthly_incomes_data = []
    monthly_expenses_data = []

    for i in range(5, -1, -1):
        # Calculate year and month i months ago
        year = today.year
        month = today.month - i
        if month <= 0:
            month += 12
            year -= 1

        dt = datetime.date(year, month, 1)
        month_name = dt.strftime('%b %Y')
        months_labels.append(month_name)

        inc_val = Income.objects.filter(user=user, date__year=year, date__month=month).aggregate(t=Sum('amount'))['t'] or 0
        exp_val = Expense.objects.filter(user=user, date__year=year, date__month=month).aggregate(t=Sum('amount'))['t'] or 0

        monthly_incomes_data.append(float(inc_val))
        monthly_expenses_data.append(float(exp_val))

    data = {
        'income_vs_expense': {
            'labels': ['Total Income', 'Total Expense'],
            'data': [float(total_inc), float(total_exp)],
        },
        'category_wise': {
            'labels': category_labels,
            'data': category_amounts,
            'colors': category_colors,
        },
        'monthly_trends': {
            'labels': months_labels,
            'income': monthly_incomes_data,
            'expenses': monthly_expenses_data,
        }
    }
    return JsonResponse(data)
