from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Income, Deduction, TaxRecord


# ----------------------------
# User Registration
# ----------------------------
def register_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("register")

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(request, "Account created successfully.")
        return redirect("login")

    return render(request, "accounts/register.html")


# ----------------------------
# User Login
# ----------------------------
def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("dashboard")

        messages.error(request, "Invalid username or password.")
        return redirect("login")

    return render(request, "accounts/login.html")


# ----------------------------
# Dashboard View
# ----------------------------
@login_required
def dashboard_view(request):

    incomes = Income.objects.filter(user=request.user).order_by("-date")[:5]
    deductions = Deduction.objects.filter(user=request.user).order_by("-date")[:5]

    total_income = Income.objects.filter(user=request.user).aggregate(
        Sum("amount")
    )["amount__sum"] or Decimal("0.00")

    total_deductions = Deduction.objects.filter(user=request.user).aggregate(
        Sum("amount")
    )["amount__sum"] or Decimal("0.00")

    recent_tax = TaxRecord.objects.filter(user=request.user).order_by("-created_at")[:5]

    context = {
        "incomes": incomes,
        "deductions": deductions,
        "total_income": total_income,
        "total_deductions": total_deductions,
        "net_income": total_income - total_deductions,
        "recent_tax": recent_tax
    }

    return render(request, "accounts/dashboard.html", context)


# ----------------------------
# Add Income
# ----------------------------
@login_required
def add_income(request):

    if request.method == "POST":

        Income.objects.create(
            user=request.user,
            source=request.POST.get("source"),
            amount=Decimal(request.POST.get("amount")),
            date=request.POST.get("date") or None,
            description=request.POST.get("description", "")
        )

        messages.success(request, "Income added successfully.")
        return redirect("dashboard")

    return render(request, "accounts/add_income.html")


# ----------------------------
# Delete Income
# ----------------------------
@login_required
def delete_income(request, income_id):

    income = get_object_or_404(Income, id=income_id, user=request.user)
    income.delete()

    messages.success(request, "Income deleted successfully.")
    return redirect("dashboard")


# ----------------------------
# Add Deduction
# ----------------------------
@login_required
def add_deduction(request):

    if request.method == "POST":

        Deduction.objects.create(
            user=request.user,
            section=request.POST.get("section"),
            amount=Decimal(request.POST.get("amount")),
            date=request.POST.get("date") or None,
            description=request.POST.get("description", "")
        )

        messages.success(request, "Deduction added successfully.")
        return redirect("dashboard")

    return render(request, "accounts/add_deduction.html")


# ----------------------------
# Delete Deduction
# ----------------------------
@login_required
def delete_deduction(request, deduction_id):

    deduction = get_object_or_404(Deduction, id=deduction_id, user=request.user)
    deduction.delete()

    messages.success(request, "Deduction deleted successfully.")
    return redirect("dashboard")


# ----------------------------
# Tax Calculation
# ----------------------------
@login_required
def calculate_tax_view(request):

    total_income = Income.objects.filter(user=request.user).aggregate(
        Sum("amount")
    )["amount__sum"] or Decimal("0.00")

    total_deductions = Deduction.objects.filter(user=request.user).aggregate(
        Sum("amount")
    )["amount__sum"] or Decimal("0.00")

    regime = request.GET.get("regime", "new")

    # Calculate taxable income (standard deduction removed)
    if regime == "old":
        taxable_income = total_income - total_deductions
    else:
        taxable_income = total_income

    if taxable_income < 0:
        taxable_income = Decimal("0.00")

    tax = Decimal("0.00")

    # New Regime Slabs
    if regime == "new":

        if taxable_income > 300000:

            if taxable_income <= 600000:
                tax = (taxable_income - 300000) * Decimal("0.05")

            elif taxable_income <= 900000:
                tax = (300000 * Decimal("0.05")) + (taxable_income - 600000) * Decimal("0.10")

            elif taxable_income <= 1200000:
                tax = (300000 * Decimal("0.05")) + (300000 * Decimal("0.10")) + (taxable_income - 900000) * Decimal("0.15")

            elif taxable_income <= 1500000:
                tax = (300000 * Decimal("0.05")) + (300000 * Decimal("0.10")) + (300000 * Decimal("0.15")) + (taxable_income - 1200000) * Decimal("0.20")

            else:
                tax = (
                    (300000 * Decimal("0.05")) +
                    (300000 * Decimal("0.10")) +
                    (300000 * Decimal("0.15")) +
                    (300000 * Decimal("0.20")) +
                    (taxable_income - 1500000) * Decimal("0.30")
                )

        if taxable_income <= 700000:
            tax = Decimal("0.00")

    # Old Regime Slabs
    else:

        if taxable_income > 250000:

            if taxable_income <= 500000:
                tax = (taxable_income - 250000) * Decimal("0.05")

            elif taxable_income <= 1000000:
                tax = (250000 * Decimal("0.05")) + (taxable_income - 500000) * Decimal("0.20")

            else:
                tax = (
                    (250000 * Decimal("0.05")) +
                    (500000 * Decimal("0.20")) +
                    (taxable_income - 1000000) * Decimal("0.30")
                )

        if taxable_income <= 500000:
            tax = Decimal("0.00")

    cess = tax * Decimal("0.04")
    total_tax = tax + cess

    monthly = total_tax / Decimal("12")
    daily = total_tax / Decimal("365")

    TaxRecord.objects.create(
        user=request.user,
        total_income=total_income,
        total_deductions=total_deductions,
        taxable_income=taxable_income,
        tax_amount=tax,
        cess=cess,
        total_tax=total_tax,
        regime=regime
    )

    context = {
        "total_income": total_income,
        "total_deductions": total_deductions,
        "taxable_income": taxable_income,
        "base_tax": tax,
        "cess": cess,
        "total_tax": total_tax,
        "monthly": monthly,
        "daily": daily,
        "regime": regime,
        "effective_tax_rate": (total_tax / total_income * 100) if total_income > 0 else 0
    }

    return render(request, "accounts/calculate_tax.html", context)


# ----------------------------
# Explore Investment Plans
# ----------------------------
@login_required
def explore_plans(request):
    return render(request, "accounts/explore_plans.html")


# ----------------------------
# Plan Detail Page
# ----------------------------
@login_required
def plan_detail(request, slug):

    plans = {
        "elss": {"name": "ELSS Mutual Funds", "return": "14%", "desc": "Tax saving under section 80C"},
        "ppf": {"name": "Public Provident Fund", "return": "7.1%", "desc": "Government backed investment"},
        "health": {"name": "Health Insurance", "return": "Coverage", "desc": "Tax benefit under section 80D"},
        "nps": {"name": "National Pension System", "return": "10-12%", "desc": "Retirement investment option"},
        "home": {"name": "Home Loan", "return": "8.5%", "desc": "Tax benefits on principal and interest"},
        "education": {"name": "Education Loan", "return": "9-11%", "desc": "Deduction on interest paid"}
    }

    context = {
        "plan": plans.get(slug)
    }

    return render(request, "accounts/plan_detail.html", context)


# ----------------------------
# Logout
# ----------------------------
def logout_view(request):
    logout(request)
    return redirect("login")