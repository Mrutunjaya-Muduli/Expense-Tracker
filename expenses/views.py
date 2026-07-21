from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from .models import Expense, Category
from .forms import ExpenseForm, CategoryForm
from .utils import ensure_default_categories

@login_required
def expense_list(request):
    expenses = Expense.objects.filter(user=request.user)

    # Search filter
    search_query = request.GET.get('search', '')
    if search_query:
        expenses = expenses.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))

    # Category filter
    category_filter = request.GET.get('category', '')
    if category_filter:
        expenses = expenses.filter(category_id=category_filter)

    # Payment Method filter
    payment_filter = request.GET.get('payment_method', '')
    if payment_filter:
        expenses = expenses.filter(payment_method=payment_filter)

    # Date range filters
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    if start_date:
        expenses = expenses.filter(date__gte=start_date)
    if end_date:
        expenses = expenses.filter(date__lte=end_date)

    # Sorting options
    sort_by = request.GET.get('sort', '-date')
    if sort_by in ['date', '-date', 'amount', '-amount', 'title']:
        expenses = expenses.order_by(sort_by)

    total_expense = expenses.aggregate(total=Sum('amount'))['total'] or 0
    categories = Category.objects.filter(Q(user=request.user) | Q(user__isnull=True))

    context = {
        'expenses': expenses,
        'total_expense': total_expense,
        'categories': categories,
        'payment_methods': Expense.PAYMENT_METHODS,
        'search_query': search_query,
        'category_filter': category_filter,
        'payment_filter': payment_filter,
        'start_date': start_date,
        'end_date': end_date,
        'sort_by': sort_by,
    }
    return render(request, 'expenses/expense_list.html', context)

@login_required
def expense_add(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST, user=request.user)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            messages.success(request, f"Expense '{expense.title}' recorded successfully!")
            return redirect('expense_list')
    else:
        form = ExpenseForm(user=request.user)
    return render(request, 'expenses/expense_form.html', {'form': form, 'title': 'Add Expense'})

@login_required
def expense_edit(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f"Expense '{expense.title}' updated successfully!")
            return redirect('expense_list')
    else:
        form = ExpenseForm(instance=expense, user=request.user)
    return render(request, 'expenses/expense_form.html', {'form': form, 'title': 'Edit Expense', 'expense': expense})

@login_required
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        title = expense.title
        expense.delete()
        messages.success(request, f"Expense '{title}' deleted successfully!")
        return redirect('expense_list')
    return render(request, 'expenses/expense_confirm_delete.html', {'expense': expense})

# Category CRUD
@login_required
def category_list(request):
    categories = Category.objects.filter(Q(user=request.user) | Q(user__isnull=True))
    return render(request, 'expenses/category_list.html', {'categories': categories})

@login_required
def category_add(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            cat = form.save(commit=False)
            cat.user = request.user
            cat.save()
            messages.success(request, f"Custom category '{cat.category_name}' created!")
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'expenses/category_form.html', {'form': form, 'title': 'Add Category'})

@login_required
def category_edit(request, pk):
    cat = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=cat)
        if form.is_valid():
            form.save()
            messages.success(request, f"Category '{cat.category_name}' updated!")
            return redirect('category_list')
    else:
        form = CategoryForm(instance=cat)
    return render(request, 'expenses/category_form.html', {'form': form, 'title': 'Edit Category', 'category': cat})

@login_required
def category_delete(request, pk):
    cat = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        name = cat.category_name
        cat.delete()
        messages.success(request, f"Category '{name}' deleted!")
        return redirect('category_list')
    return render(request, 'expenses/category_confirm_delete.html', {'category': cat})
