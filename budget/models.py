from django.db import models
from django.contrib.auth.models import User
from expenses.models import Category

class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    month = models.CharField(max_length=7, help_text="Format: YYYY-MM (e.g. 2026-07)")
    total_budget = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True, related_name='budgets', help_text="Leave blank for overall monthly budget")

    class Meta:
        ordering = ['-month']
        unique_together = ('user', 'month', 'category')

    def __str__(self):
        cat_str = f" ({self.category.category_name})" if self.category else " (Overall)"
        return f"{self.user.username} - {self.month}{cat_str}: {self.total_budget}"
