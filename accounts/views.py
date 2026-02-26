from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Income, Deduction, TaxRecord


# ------------------ REGISTER ------------------
def register_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect('register')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        user.save()

        messages.success(request, "Account created successfully!")
        return redirect('login')

    return render(request, 'accounts/register.html')


# ------------------ LOGIN ------------------
def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password")
            return redirect('login')

    return render(request, 'accounts/login.html')


# ------------------ DASHBOARD ------------------
@login_required
def dashboard_view(request):
    incomes = Income.objects.filter(user=request.user)
    deductions = Deduction.objects.filter(user=request.user)

    total_income = incomes.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    total_deductions = deductions.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')

    context = {
        'incomes': incomes,
        'deductions': deductions,
        'total_income': total_income,
        'total_deductions': total_deductions,
    }

    return render(request, 'accounts/dashboard.html', context)


# ------------------ ADD INCOME ------------------
@login_required
def add_income(request):
    if request.method == "POST":
        source = request.POST.get('source')
        amount = request.POST.get('amount')
        date = request.POST.get('date')
        description = request.POST.get('description')

        Income.objects.create(
            user=request.user,
            source=source,
            amount=Decimal(amount),
            date=date,
            description=description
        )

        messages.success(request, "Income added successfully!")
        return redirect('dashboard')

    return render(request, 'accounts/add_income.html')


# ------------------ DELETE INCOME ------------------
@login_required
def delete_income(request, income_id):
    income = get_object_or_404(Income, id=income_id, user=request.user)
    income.delete()
    messages.success(request, "Income deleted successfully!")
    return redirect('dashboard')


# ------------------ ADD DEDUCTION ------------------
@login_required
def add_deduction(request):
    if request.method == "POST":
        section = request.POST.get('section')
        amount = request.POST.get('amount')
        date = request.POST.get('date')
        description = request.POST.get('description')

        Deduction.objects.create(
            user=request.user,
            section=section,
            amount=Decimal(amount),
            date=date,
            description=description
        )

        messages.success(request, "Deduction added successfully!")
        return redirect('dashboard')

    return render(request, 'accounts/add_deduction.html')


# ------------------ DELETE DEDUCTION ------------------
@login_required
def delete_deduction(request, deduction_id):
    deduction = get_object_or_404(Deduction, id=deduction_id, user=request.user)
    deduction.delete()
    messages.success(request, "Deduction deleted successfully!")
    return redirect('dashboard')


# ------------------ TAX CALCULATION ------------------
@login_required
def calculate_tax_view(request):

    incomes = Income.objects.filter(user=request.user)
    deductions = Deduction.objects.filter(user=request.user)

    total_income = incomes.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    total_deductions = deductions.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')

    # Standard Deduction (New Regime)
    standard_deduction = Decimal('50000')

    taxable_income = total_income - standard_deduction
    if taxable_income < 0:
        taxable_income = Decimal('0.00')

    tax = Decimal('0.00')

    # New Regime Slabs
    if taxable_income <= 300000:
        tax = Decimal('0.00')

    elif taxable_income <= 600000:
        tax = (taxable_income - 300000) * Decimal('0.05')

    elif taxable_income <= 900000:
        tax = (300000 * Decimal('0.05')) + \
              (taxable_income - 600000) * Decimal('0.10')

    elif taxable_income <= 1200000:
        tax = (300000 * Decimal('0.05')) + \
              (300000 * Decimal('0.10')) + \
              (taxable_income - 900000) * Decimal('0.15')

    elif taxable_income <= 1500000:
        tax = (300000 * Decimal('0.05')) + \
              (300000 * Decimal('0.10')) + \
              (300000 * Decimal('0.15')) + \
              (taxable_income - 1200000) * Decimal('0.20')

    else:
        tax = (300000 * Decimal('0.05')) + \
              (300000 * Decimal('0.10')) + \
              (300000 * Decimal('0.15')) + \
              (300000 * Decimal('0.20')) + \
              (taxable_income - 1500000) * Decimal('0.30')

    # 4% Cess
    cess = tax * Decimal('0.04')
    total_tax = tax + cess

    # Save Tax Record
    TaxRecord.objects.create(
        user=request.user,
        total_income=total_income,
        total_deductions=total_deductions,
        taxable_income=taxable_income,
        tax_amount=tax,
        cess=cess,
        total_tax=total_tax,
        regime='new'
    )

    context = {
        'total_income': total_income,
        'total_deductions': total_deductions,
        'taxable_income': taxable_income,
        'tax': tax,
        'cess': cess,
        'total_tax': total_tax,
    }

    return render(request, 'accounts/tax_result.html', context)


# ------------------ LOGOUT ------------------
def logout_view(request):
    logout(request)
    return redirect('login')