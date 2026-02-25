from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Income


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

    total_income = incomes.aggregate(Sum('amount'))['amount__sum'] or 0

    context = {
        'incomes': incomes,
        'total_income': total_income,
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
            amount=amount,
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


# ------------------ LOGOUT ------------------
def logout_view(request):
    logout(request)
    return redirect('login')