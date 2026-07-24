from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from decimal import Decimal
import datetime

from .models import Group, GroupExpense, GroupExpenseSplit
from .forms import GroupExpenseForm

@login_required
def group_list_view(request):
    user = request.user
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        # 1. Create Group Action
        if action == 'create':
            name = request.POST.get('name')
            description = request.POST.get('description', '')
            if name:
                group = Group.objects.create(
                    name=name,
                    description=description,
                    created_by=user
                )
                group.members.add(user)
                messages.success(request, f"Group '{name}' created successfully!")
                return redirect('group_detail', group_id=group.id)
            else:
                messages.error(request, "Group name is required.")
                
        # 2. Join Group Action
        elif action == 'join':
            invite_code = request.POST.get('invite_code', '').strip().upper()
            if invite_code:
                group = Group.objects.filter(invite_code=invite_code).first()
                if group:
                    if user in group.members.all():
                        messages.info(request, f"You are already a member of '{group.name}'.")
                    else:
                        group.members.add(user)
                        messages.success(request, f"Successfully joined the group '{group.name}'!")
                    return redirect('group_detail', group_id=group.id)
                else:
                    messages.error(request, "Invalid invite code. Group not found.")
            else:
                messages.error(request, "Please enter an invite code.")
                
    groups = user.shared_groups.all()
    # Get user profile currency
    currency_symbol = user.profile.currency if hasattr(user, 'profile') else '₹'
    
    context = {
        'groups': groups,
        'currency_symbol': currency_symbol
    }
    return render(request, 'groups/group_list.html', context)

@login_required
def group_detail_view(request, group_id):
    user = request.user
    group = get_object_or_404(Group, id=group_id)
    
    # Security check: verify user is in this group
    if user not in group.members.all():
        messages.error(request, "You do not have permission to view this group.")
        return redirect('group_list')
        
    # Handle adding a member directly
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add_member':
            user_id = request.POST.get('user_id')
            if user_id:
                member_to_add = get_object_or_404(User, id=user_id)
                group.members.add(member_to_add)
                messages.success(request, f"Added {member_to_add.username} to the group successfully!")
            return redirect('group_detail', group_id=group.id)
            
    # Calculate group balances
    members = group.members.all()
    # Initialize dict to track net balance of each user
    balances = {member: Decimal('0.00') for member in members}
    
    # 1. Process all group expenses
    expenses = group.expenses.all().prefetch_related('splits')
    for exp in expenses:
        # Add total amount paid to the payer
        if exp.paid_by in balances:
            balances[exp.paid_by] += exp.amount
        
        # Deduct split amount from each split member
        for split in exp.splits.all():
            if split.user in balances:
                balances[split.user] -= split.amount
            
    # Format member balance display structure
    member_balances = []
    currency_symbol = user.profile.currency if hasattr(user, 'profile') else '₹'
    
    for member in members:
        bal = balances[member]
        member_balances.append({
            'user': member,
            'balance': bal,
            'is_creditor': bal > 0,
            'is_debtor': bal < 0,
            'is_zero': bal == 0
        })

    # 2. Run Splitwise Minimization Settlement Algorithm
    # Group users into creditors (positive balance) and debtors (negative balance)
    creditors = []
    debtors = []
    
    for member, bal in balances.items():
        if bal > 0.01:
            creditors.append({'user': member, 'balance': bal})
        elif bal < -0.01:
            debtors.append({'user': member, 'balance': abs(bal)})
            
    # Sort creditors descending, debtors descending (by absolute value)
    creditors.sort(key=lambda x: x['balance'], reverse=True)
    debtors.sort(key=lambda x: x['balance'], reverse=True)
    
    suggested_settlements = []
    
    c_idx = 0
    d_idx = 0
    
    while c_idx < len(creditors) and d_idx < len(debtors):
        creditor = creditors[c_idx]
        debtor = debtors[d_idx]
        
        payment = min(creditor['balance'], debtor['balance'])
        
        suggested_settlements.append({
            'from_user': debtor['user'],
            'to_user': creditor['user'],
            'amount': payment
        })
        
        creditor['balance'] -= payment
        debtor['balance'] -= payment
        
        if creditor['balance'] < 0.01:
            c_idx += 1
        if debtor['balance'] < 0.01:
            d_idx += 1
            
    non_members = User.objects.exclude(id__in=group.members.values_list('id', flat=True))
            
    context = {
        'group': group,
        'expenses': expenses,
        'member_balances': member_balances,
        'suggested_settlements': suggested_settlements,
        'non_members': non_members,
        'currency_symbol': currency_symbol
    }
    return render(request, 'groups/group_detail.html', context)

@login_required
def group_expense_add_view(request, group_id):
    user = request.user
    group = get_object_or_404(Group, id=group_id)
    
    if user not in group.members.all():
        messages.error(request, "Access denied.")
        return redirect('group_list')
        
    if request.method == 'POST':
        form = GroupExpenseForm(request.POST, group=group)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.group = group
            expense.save()
            
            # Split expense among selected users
            split_with_users = form.cleaned_data['split_with']
            total_amount = expense.amount
            num_users = len(split_with_users)
            
            if num_users > 0:
                # Divide amount equally, handle division precision
                base_share = (total_amount / num_users).quantize(Decimal('0.01'))
                
                # Check for rounding differences
                rounding_diff = total_amount - (base_share * num_users)
                
                for idx, split_user in enumerate(split_with_users):
                    # Allocate rounding difference to the first user
                    share = base_share
                    if idx == 0:
                        share += rounding_diff
                        
                    GroupExpenseSplit.objects.create(
                        group_expense=expense,
                        user=split_user,
                        amount=share
                    )
            
            messages.success(request, f"Expense '{expense.title}' added successfully!")
            return redirect('group_detail', group_id=group.id)
        else:
            messages.error(request, "Failed to add expense. Please correct the fields.")
    else:
        form = GroupExpenseForm(group=group, initial={
            'paid_by': user,
            'date': datetime.date.today()
        })
        
    context = {
        'group': group,
        'form': form
    }
    return render(request, 'groups/expense_form.html', context)

@login_required
def group_expense_delete_view(request, group_id, expense_id):
    user = request.user
    group = get_object_or_404(Group, id=group_id)
    
    if user not in group.members.all():
        messages.error(request, "Access denied.")
        return redirect('group_list')
        
    expense = get_object_or_404(GroupExpense, id=expense_id, group=group)
    title = expense.title
    expense.delete()
    messages.success(request, f"Expense '{title}' deleted.")
    return redirect('group_detail', group_id=group.id)

@login_required
def settle_payment_view(request, group_id):
    user = request.user
    group = get_object_or_404(Group, id=group_id)
    
    if user not in group.members.all():
        messages.error(request, "Access denied.")
        return redirect('group_list')
        
    if request.method == 'POST':
        from_user_id = request.POST.get('from_user_id')
        to_user_id = request.POST.get('to_user_id')
        amount_str = request.POST.get('amount')
        
        try:
            from_user = User.objects.get(id=from_user_id)
            to_user = User.objects.get(id=to_user_id)
            amount = Decimal(amount_str)
            
            # 1. Create a special Settlement Expense
            title = f"Settled debt to {to_user.username}"
            expense = GroupExpense.objects.create(
                group=group,
                paid_by=from_user,
                title=title,
                amount=amount,
                date=datetime.date.today(),
                description=f"Recorded settlement payment from {from_user.username} to {to_user.username}"
            )
            
            # 2. Split 100% of this expense to the receiver
            GroupExpenseSplit.objects.create(
                group_expense=expense,
                user=to_user,
                amount=amount
            )
            
            messages.success(request, f"Settlement payment of {amount} from {from_user.username} to {to_user.username} recorded successfully!")
            
        except (User.DoesNotExist, ValueError, TypeError) as e:
            messages.error(request, "Failed to record settlement payment.")
            
    return redirect('group_detail', group_id=group.id)
