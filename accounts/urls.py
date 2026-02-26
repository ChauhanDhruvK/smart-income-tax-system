from django.urls import path
from . import views

urlpatterns = [
        path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

    path('add-income/', views.add_income, name='add_income'),
    path('delete-income/<int:income_id>/', views.delete_income, name='delete_income'),

    path('add-deduction/', views.add_deduction, name='add_deduction'),
    path('delete-deduction/<int:deduction_id>/', views.delete_deduction, name='delete_deduction'),

    path('calculate-tax/', views.calculate_tax_view, name='calculate_tax'),

]