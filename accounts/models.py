from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
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
    cess = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    surcharge = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_tax = models.DecimalField(max_digits=12, decimal_places=2)
    regime = models.CharField(max_length=10, default='new')
    created_at = models.DateTimeField(auto_now_add=True)  # This is the field name
    
    def __str__(self):
        return f"{self.user.username} - {self.created_at.date()}"

class UserProfile(models.Model):
    """Extended user profile model"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    pan_number = models.CharField(max_length=10, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

# Auto-create profile when user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)