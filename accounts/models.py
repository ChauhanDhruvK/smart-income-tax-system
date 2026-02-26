from django.db import models
from django.contrib.auth.models import User


# ------------------ INCOME MODEL ------------------
class Income(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    source = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.source} - {self.amount}"


# ------------------ DEDUCTION MODEL ------------------
class Deduction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    section = models.CharField(max_length=50)   # Example: 80C, 80D
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.section} - {self.amount}"


# ------------------ TAX RECORD MODEL ------------------
class TaxRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    total_income = models.DecimalField(max_digits=12, decimal_places=2)
    total_deductions = models.DecimalField(max_digits=12, decimal_places=2)

    taxable_income = models.DecimalField(max_digits=12, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2)
    cess = models.DecimalField(max_digits=12, decimal_places=2)
    total_tax = models.DecimalField(max_digits=12, decimal_places=2)

    regime = models.CharField(max_length=20, choices=[
        ('old', 'Old Regime'),
        ('new', 'New Regime')
    ], default='new')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - Tax Record - {self.created_at.date()}"