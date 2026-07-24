from django.db import models
from django.contrib.auth.models import User
import secrets
import string

class Group(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default='')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_groups')
    created_at = models.DateTimeField(auto_now_add=True)
    members = models.ManyToManyField(User, related_name='shared_groups')
    invite_code = models.CharField(max_length=10, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.invite_code:
            characters = string.ascii_uppercase + string.digits
            while True:
                code = ''.join(secrets.choice(characters) for _ in range(6))
                # Check if this code already exists in db
                if not Group.objects.filter(invite_code=code).exists():
                    self.invite_code = code
                    break
        super().save(*args, **kwargs)

    @property
    def is_settled(self):
        members = self.members.all()
        if not members.exists():
            return True
        balances = {member: 0.0 for member in members}
        expenses = self.expenses.all().prefetch_related('splits')
        for exp in expenses:
            if exp.paid_by in balances:
                balances[exp.paid_by] += float(exp.amount)
            for split in exp.splits.all():
                if split.user in balances:
                    balances[split.user] -= float(split.amount)
        for bal in balances.values():
            if abs(bal) > 0.01:
                return False
        return True

    def __str__(self):
        return self.name

class GroupExpense(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='expenses')
    paid_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='paid_group_expenses')
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    description = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.title} in {self.group.name} - {self.amount}"

class GroupExpenseSplit(models.Model):
    group_expense = models.ForeignKey(GroupExpense, on_delete=models.CASCADE, related_name='splits')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_splits')
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.user.username}'s share of {self.group_expense.title} - {self.amount}"
