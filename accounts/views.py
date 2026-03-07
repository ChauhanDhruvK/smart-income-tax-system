from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Income, Deduction, TaxRecord

# Register
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
        messages.success(request, "Account created successfully!")
        return redirect('login')
    return render(request, 'accounts/register.html')

# Login
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

# Dashboard
@login_required
def dashboard_view(request):
    incomes = Income.objects.filter(user=request.user).order_by('-date')[:5]
    deductions = Deduction.objects.filter(user=request.user).order_by('-date')[:5]
    
    total_income = Income.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    total_deductions = Deduction.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    
    # Fix: Use created_at instead of calculated_date
    recent_tax = TaxRecord.objects.filter(user=request.user).order_by('-created_at')[:5]

    context = {
        'incomes': incomes,
        'deductions': deductions,
        'total_income': total_income,
        'total_deductions': total_deductions,
        'net_income': total_income - total_deductions,
        'recent_tax': recent_tax,
        'income_count': Income.objects.filter(user=request.user).count(),
        'deduction_count': Deduction.objects.filter(user=request.user).count(),
    }
    return render(request, 'accounts/dashboard.html', context)

# Add Income
@login_required
def add_income(request):
    if request.method == "POST":
        Income.objects.create(
            user=request.user,
            source=request.POST.get('source'),
            amount=Decimal(request.POST.get('amount')),
            date=request.POST.get('date') or None,
            description=request.POST.get('description', '')
        )
        messages.success(request, "Income added successfully!")
        return redirect('dashboard')
    return render(request, 'accounts/add_income.html')

# Delete Income
@login_required
def delete_income(request, income_id):
    income = get_object_or_404(Income, id=income_id, user=request.user)
    income.delete()
    messages.success(request, "Income deleted!")
    return redirect('dashboard')

# Add Deduction
@login_required
def add_deduction(request):
    if request.method == "POST":
        Deduction.objects.create(
            user=request.user,
            section=request.POST.get('section'),
            amount=Decimal(request.POST.get('amount')),
            date=request.POST.get('date') or None,
            description=request.POST.get('description', '')
        )
        messages.success(request, "Deduction added successfully!")
        return redirect('dashboard')
    return render(request, 'accounts/add_deduction.html')

# Delete Deduction
@login_required
def delete_deduction(request, deduction_id):
    deduction = get_object_or_404(Deduction, id=deduction_id, user=request.user)
    deduction.delete()
    messages.success(request, "Deduction deleted!")
    return redirect('dashboard')

# Calculate Tax
@login_required
def calculate_tax_view(request):
    total_income = Income.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    total_deductions = Deduction.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    
    # Simple tax calculation (new regime)
    taxable_income = total_income - Decimal('50000')  # Standard deduction
    if taxable_income < 0:
        taxable_income = Decimal('0.00')
    
    tax = Decimal('0.00')
    if taxable_income > 300000:
        if taxable_income <= 600000:
            tax = (taxable_income - 300000) * Decimal('0.05')
        elif taxable_income <= 900000:
            tax = (300000 * Decimal('0.05')) + (taxable_income - 600000) * Decimal('0.10')
        elif taxable_income <= 1200000:
            tax = (300000 * Decimal('0.05')) + (300000 * Decimal('0.10')) + (taxable_income - 900000) * Decimal('0.15')
        elif taxable_income <= 1500000:
            tax = (300000 * Decimal('0.05')) + (300000 * Decimal('0.10')) + (300000 * Decimal('0.15')) + (taxable_income - 1200000) * Decimal('0.20')
        else:
            tax = (300000 * Decimal('0.05')) + (300000 * Decimal('0.10')) + (300000 * Decimal('0.15')) + (300000 * Decimal('0.20')) + (taxable_income - 1500000) * Decimal('0.30')
    
    # Rebate for income up to 7 lakhs
    if taxable_income <= 700000:
        tax = Decimal('0.00')
    
    cess = tax * Decimal('0.04')
    total_tax = tax + cess
    
    # Save record
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
        'effective_tax_rate': (total_tax / total_income * 100) if total_income > 0 else 0,
    }
    return render(request, 'accounts/tax_result.html', context)

# Explore Plans
@login_required
def explore_plans(request):
    return render(request, 'accounts/explore_plans.html')

# Logout
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def plan_detail(request, plan_type):
    plans = {
        'elss': {'name': 'ELSS Mutual Funds', 'return': '14%', 'desc': 'Tax saving under 80C with highest returns'},
        'ppf': {'name': 'PPF', 'return': '7.1%', 'desc': 'Risk-free government backed investment'},
        'health': {'name': 'Health Insurance', 'return': 'Coverage', 'desc': 'Tax benefit under 80D'},
        'nps': {'name': 'NPS', 'return': '10-12%', 'desc': 'National Pension System with extra benefits'},
        'home': {'name': 'Home Loan', 'return': '8.5%', 'desc': 'Tax benefits on principal and interest'},
        'education': {'name': 'Education Loan', 'return': '9-11%', 'desc': 'Deduction on interest paid'}
    }
    plan = plans.get(plan_type, plans['elss'])
    context = {
        'plan': plan,
        'plan_type': plan_type
    }
    return render(request, 'accounts/plan_detail.html', context)

@login_required
def calculate_tax_view(request):
    total_income = Income.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    total_deductions = Deduction.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    
    # Get regime from request
    regime = request.GET.get('regime', 'new')
    
    # Simple tax calculation
    if regime == 'old':
        taxable_income = total_income - total_deductions - Decimal('50000')  # Standard deduction
    else:
        taxable_income = total_income - Decimal('50000')  # New regime with standard deduction
    
    if taxable_income < 0:
        taxable_income = Decimal('0.00')
    
    # Calculate tax based on slabs
    tax = Decimal('0.00')
    surcharge = Decimal('0.00')
    
    if regime == 'new':
        # New regime slabs
        if taxable_income > 300000:
            if taxable_income <= 600000:
                tax = (taxable_income - 300000) * Decimal('0.05')
            elif taxable_income <= 900000:
                tax = (300000 * Decimal('0.05')) + (taxable_income - 600000) * Decimal('0.10')
            elif taxable_income <= 1200000:
                tax = (300000 * Decimal('0.05')) + (300000 * Decimal('0.10')) + (taxable_income - 900000) * Decimal('0.15')
            elif taxable_income <= 1500000:
                tax = (300000 * Decimal('0.05')) + (300000 * Decimal('0.10')) + (300000 * Decimal('0.15')) + (taxable_income - 1200000) * Decimal('0.20')
            else:
                tax = (300000 * Decimal('0.05')) + (300000 * Decimal('0.10')) + (300000 * Decimal('0.15')) + (300000 * Decimal('0.20')) + (taxable_income - 1500000) * Decimal('0.30')
        
        # Rebate for income up to 7 lakhs
        if taxable_income <= 700000:
            tax = Decimal('0.00')
    else:
        # Old regime slabs
        if taxable_income > 250000:
            if taxable_income <= 500000:
                tax = (taxable_income - 250000) * Decimal('0.05')
            elif taxable_income <= 1000000:
                tax = (250000 * Decimal('0.05')) + (taxable_income - 500000) * Decimal('0.20')
            else:
                tax = (250000 * Decimal('0.05')) + (500000 * Decimal('0.20')) + (taxable_income - 1000000) * Decimal('0.30')
        
        # Rebate for income up to 5 lakhs
        if taxable_income <= 500000:
            tax = Decimal('12500') if tax > Decimal('12500') else tax
    
    # Add surcharge for high income (simplified)
    if taxable_income > 5000000:
        surcharge = tax * Decimal('0.10')
    
    # Health and Education Cess
    cess = (tax + surcharge) * Decimal('0.04')
    total_tax = tax + surcharge + cess
    
    # Save record
    TaxRecord.objects.create(
        user=request.user,
        total_income=total_income,
        total_deductions=total_deductions,
        taxable_income=taxable_income,
        tax_amount=tax,
        surcharge=surcharge,
        cess=cess,
        total_tax=total_tax,
        regime=regime
    )
    
    context = {
        'total_income': total_income,
        'total_deductions': total_deductions,
        'taxable_income': taxable_income,
        'tax': tax,
        'surcharge': surcharge,
        'cess': cess,
        'total_tax': total_tax,
        'regime': regime,
        'effective_tax_rate': (total_tax / total_income * 100) if total_income > 0 else 0,
    }
    return render(request, 'accounts/calculate_tax.html', context)


def plan_detail(request, slug):
    plans = {
        'elss':      {'plan_name': 'ELSS Mutual Funds',        'section_label': 'Section 80C', 'tagline': 'Equity Linked Savings Scheme', 'rate_label': 'Expected Return', 'rate': '~14%', 'rate_sub': 'market-linked', 'max_deduction': '₹1,50,000', 'lock_in': '3 years', 'tax_on_returns': 'LTCG above ₹1L', 'regime': 'Old Regime', 'risk_label': 'High', 'risk_color': '#dc2626', 'risk_pct': 85},
        'ppf':       {'plan_name': 'Public Provident Fund',    'section_label': 'Section 80C', 'tagline': 'Government backed · Risk-free', 'rate_label': 'Current Rate', 'rate': '7.1%', 'rate_sub': 'tax-free interest', 'max_deduction': '₹1,50,000', 'lock_in': '15 years', 'tax_on_returns': 'Tax-free (EEE)', 'regime': 'Old Regime', 'risk_label': 'Low', 'risk_color': '#16a34a', 'risk_pct': 12},
        'health':    {'plan_name': 'Health Insurance',         'section_label': 'Section 80D', 'tagline': 'Protect self & family', 'rate_label': 'Benefit', 'rate': 'Coverage', 'rate_sub': 'cashless hospitalisation', 'max_deduction': '₹75,000', 'lock_in': 'None', 'tax_on_returns': 'N/A', 'regime': 'Old Regime', 'risk_label': 'Low', 'risk_color': '#16a34a', 'risk_pct': 10},
        'nps':       {'plan_name': 'National Pension System',  'section_label': '80CCD(1B)', 'tagline': 'Build retirement corpus', 'rate_label': 'Expected Return', 'rate': '10–12%', 'rate_sub': 'market-linked', 'max_deduction': '₹50,000', 'lock_in': 'Till age 60', 'tax_on_returns': 'Annuity taxable', 'regime': 'Old Regime', 'risk_label': 'Medium', 'risk_color': '#d97706', 'risk_pct': 50},
        'home':      {'plan_name': 'Home Loan',                'section_label': 'Sec 24 & 80C', 'tagline': 'Own your dream property', 'rate_label': 'Interest Rate', 'rate': '8.5%', 'rate_sub': 'current avg rate', 'max_deduction': '₹3,50,000', 'lock_in': 'Loan tenure', 'tax_on_returns': 'N/A', 'regime': 'Old Regime', 'risk_label': 'Low', 'risk_color': '#16a34a', 'risk_pct': 15},
        'education': {'plan_name': 'Education Loan',           'section_label': 'Section 80E', 'tagline': 'Fund higher education', 'rate_label': 'Interest Rate', 'rate': '9–11%', 'rate_sub': 'varies by lender', 'max_deduction': 'No limit', 'lock_in': '8 years (deduction)', 'tax_on_returns': 'N/A', 'regime': 'Old Regime', 'risk_label': 'Low', 'risk_color': '#16a34a', 'risk_pct': 10},
    }
    context = plans.get(slug, {})
    context['plan_slug'] = slug
    context['overview'] = "..."   # add per plan
    return render(request, 'plan_detail.html', context)