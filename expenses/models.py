from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='categories')
    category_name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, default='bi-tag')
    color = models.CharField(max_length=20, default='#4e73df')

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['category_name']

    def __str__(self):
        return self.category_name

class Expense(models.Model):
    PAYMENT_METHODS = [
        ('Cash', 'Cash'),
        ('Credit Card', 'Credit Card'),
        ('Debit Card', 'Debit Card'),
        ('UPI/Bank Transfer', 'UPI/Bank Transfer'),
        ('Other', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses')
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='expenses')
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHODS, default='Cash')
    date = models.DateField()
    description = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-date', '-id']

    def __str__(self):
        return f"{self.title} - {self.amount}"
