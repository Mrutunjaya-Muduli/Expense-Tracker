import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from .models import Budget
from .forms import BudgetForm
from expenses.models import Expense, Category

@login_required
def budget_list(request):
    selected_month = request.GET.get('month', datetime.date.today().strftime('%Y-%m'))
    try:
        year_str, month_str = selected_month.split('-')
        year, month_int = int(year_str), int(month_str)
    except Exception:
        today = datetime.date.today()
        year, month_int = today.year, today.month
        selected_month = today.strftime('%Y-%m')

    # Get overall budget for selected month
    overall_budget_obj = Budget.objects.filter(user=request.user, month=selected_month, category__isnull=True).first()
    
    # Calculate total monthly expenses
    total_monthly_expenses = Expense.objects.filter(
        user=request.user,
        date__year=year,
        date__month=month_int
    ).aggregate(total=Sum('amount'))['total'] or 0

    overall_budget = overall_budget_obj.total_budget if overall_budget_obj else 0
    overall_remaining = overall_budget - total_monthly_expenses
    overall_percentage = round((total_monthly_expenses / overall_budget * 100), 1) if overall_budget > 0 else 0
    is_overall_over_budget = total_monthly_expenses > overall_budget if overall_budget > 0 else False

    # Category budgets & progress
    category_budgets = Budget.objects.filter(user=request.user, month=selected_month, category__isnull=False)
    category_progress_list = []

    for b in category_budgets:
        cat_expenses = Expense.objects.filter(
            user=request.user,
            category=b.category,
            date__year=year,
            date__month=month_int
        ).aggregate(total=Sum('amount'))['total'] or 0

        percent = round((cat_expenses / b.total_budget * 100), 1) if b.total_budget > 0 else 0
        rem = b.total_budget - cat_expenses
        is_over = cat_expenses > b.total_budget

        category_progress_list.append({
            'budget_id': b.id,
            'category': b.category,
            'total_budget': b.total_budget,
            'spent': cat_expenses,
            'remaining': rem,
            'percentage': percent,
            'is_over': is_over
        })

    # Available months with budgets
    existing_months = Budget.objects.filter(user=request.user).values_list('month', flat=True).distinct()
    if selected_month not in existing_months:
        existing_months = sorted(list(set(list(existing_months) + [selected_month])), reverse=True)

    context = {
        'selected_month': selected_month,
        'existing_months': existing_months,
        'overall_budget_obj': overall_budget_obj,
        'overall_budget': overall_budget,
        'total_monthly_expenses': total_monthly_expenses,
        'overall_remaining': overall_remaining,
        'overall_percentage': overall_percentage,
        'is_overall_over_budget': is_overall_over_budget,
        'category_progress_list': category_progress_list,
    }
    return render(request, 'budget/budget_list.html', context)

@login_required
def budget_add_or_edit(request, pk=None):
    budget_instance = get_object_or_404(Budget, pk=pk, user=request.user) if pk else None
    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget_instance, user=request.user)
        if form.is_valid():
            b = form.save(commit=False)
            b.user = request.user
            # Check unique constraint manually to give nice error if duplicate exists
            duplicate = Budget.objects.filter(user=request.user, month=b.month, category=b.category).exclude(pk=b.pk if pk else None).first()
            if duplicate:
                messages.error(request, f"A budget for '{b.month}' ({b.category.category_name if b.category else 'Overall'}) already exists.")
            else:
                b.save()
                messages.success(request, f"Budget saved for {b.month}!")
                return redirect('budget_list')
    else:
        form = BudgetForm(instance=budget_instance, user=request.user)
    
    return render(request, 'budget/budget_form.html', {'form': form, 'title': 'Edit Budget' if pk else 'Set Budget'})

@login_required
def budget_delete(request, pk):
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    if request.method == 'POST':
        month = budget.month
        cat_name = budget.category.category_name if budget.category else 'Overall'
        budget.delete()
        messages.success(request, f"Budget for {month} ({cat_name}) deleted.")
        return redirect('budget_list')
    return render(request, 'budget/budget_confirm_delete.html', {'budget': budget})
