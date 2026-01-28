from django.urls import path
from . import views


app_name = 'payroll'

urlpatterns = [
    path('', views.dashboard, name='admin_dashboard'),
    path('payee/', views.payee_dashboard, name='payee_dashboard'),
    path('profile/', views.payee_profile, name='payee_profile'),
    path('banking/', views.manage_bank_account, name='manage_bank_account'),
    path('admin/banking/', views.admin_manage_bank_account, name='admin_manage_bank_account'),
    path('banking/approve/', views.approve_bank_accounts, name='approve_bank_accounts'),
    path('payee/create/', views.admin_create_payee, name='admin_create_payee'),
    path('structure/create/', views.create_salary_structure, name='create_salary_structure'),
    path('components/manage/', views.manage_salary_components, name='manage_salary_components'),
    path('generate/', views.generate_payroll, name='generate_payroll'),
    path('periods/', views.payroll_list, name='payroll_list'),
    path('period/<int:period_id>/', views.payroll_detail, name='payroll_detail'),
    path('period/<int:period_id>/approve/', views.approve_lock_payroll, name='approve_lock_payroll'),
    path('period/<int:period_id>/process-payments/', views.process_payments, name='process_payments'),
    path('period/<int:period_id>/payment-status/', views.payment_status, name='payment_status'),
    path('transaction/<int:transaction_id>/retry/', views.retry_payment, name='retry_payment'),
    path('webhook/paystack/', views.paystack_webhook, name='paystack_webhook'),
    path('payslip/<int:record_id>/', views.payslip_view, name='payslip_view'),
    
    # Payee Management
    path('payees/', views.admin_payee_list, name='admin_payee_list'),
    path('payee/<int:payee_id>/toggle/', views.toggle_payee_status, name='toggle_payee_status'),
    path('payee/<int:payee_id>/delete/', views.delete_payee, name='delete_payee'),
    path('record/<int:record_id>/delete/', views.delete_payroll_record, name='delete_payroll_record'),
]
