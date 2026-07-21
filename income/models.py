from django.db import models
from django.contrib.auth.models import User

class Income(models.Model):
    SOURCE_CHOICES = [
        ('Salary', 'Salary'),
        ('Freelance', 'Freelance'),
        ('Business', 'Business'),
        ('Investment', 'Investment'),
        ('Gift', 'Gift'),
        ('Other', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='incomes')
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES, default='Salary')
    date = models.DateField()
    description = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-date', '-id']

    def __str__(self):
        return f"{self.title} - {self.amount}"
