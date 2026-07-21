from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from .models import Income
from .forms import IncomeForm

@login_required
def income_list(request):
    incomes = Income.objects.filter(user=request.user)
    
    # Search filter
    search_query = request.GET.get('search', '')
    if search_query:
        incomes = incomes.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))
    
    # Source filter
    source_filter = request.GET.get('source', '')
    if source_filter:
        incomes = incomes.filter(source=source_filter)
        
    # Date range filters
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    if start_date:
        incomes = incomes.filter(date__gte=start_date)
    if end_date:
        incomes = incomes.filter(date__lte=end_date)

    # Sorting
    sort_by = request.GET.get('sort', '-date')
    if sort_by in ['date', '-date', 'amount', '-amount', 'title']:
        incomes = incomes.order_by(sort_by)

    total_income = incomes.aggregate(total=Sum('amount'))['total'] or 0

    context = {
        'incomes': incomes,
        'total_income': total_income,
        'search_query': search_query,
        'source_filter': source_filter,
        'start_date': start_date,
        'end_date': end_date,
        'sort_by': sort_by,
        'sources': Income.SOURCE_CHOICES,
    }
    return render(request, 'income/income_list.html', context)

@login_required
def income_add(request):
    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            income = form.save(commit=False)
            income.user = request.user
            income.save()
            messages.success(request, f"Income '{income.title}' added successfully!")
            return redirect('income_list')
    else:
        form = IncomeForm()
    return render(request, 'income/income_form.html', {'form': form, 'title': 'Add Income'})

@login_required
def income_edit(request, pk):
    income = get_object_or_404(Income, pk=pk, user=request.user)
    if request.method == 'POST':
        form = IncomeForm(request.POST, instance=income)
        if form.is_valid():
            form.save()
            messages.success(request, f"Income '{income.title}' updated successfully!")
            return redirect('income_list')
    else:
        form = IncomeForm(instance=income)
    return render(request, 'income/income_form.html', {'form': form, 'title': 'Edit Income', 'income': income})

@login_required
def income_delete(request, pk):
    income = get_object_or_404(Income, pk=pk, user=request.user)
    if request.method == 'POST':
        title = income.title
        income.delete()
        messages.success(request, f"Income '{title}' deleted successfully!")
        return redirect('income_list')
    return render(request, 'income/income_confirm_delete.html', {'income': income})
