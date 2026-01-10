from django.urls import path
from . import views  


app_name = 'loans'

urlpatterns = [
    
    # =========================
    # ADMIN – LOANS
    # =========================
    path(
        "admin/staff/loan-payroll/dashboard/", views.staff_loan_payroll_dashboard, name="staff_loan_payroll_dashboard"
    ),

    path(
        "admin/admin/loan-payroll/dashboard", views.admin_loan_payroll_dashboard, name="admin_loan_payroll_dashboard"
    ),

    path(
        "admin/loans/", views.admin_loans_list, name="admin_loans_list"
    ),

    path(
        "admin/loan/<int:loan_id>/approve/", views.approve_loan, name="approve_loan"
    ),

    path(
        "admin/loan/<int:loan_id>/reject/", views.reject_loan, name="reject_loan"
    ),

    path(
        "admin/loan/<int:loan_id>/schedule/", views.loan_amortization_table, name="loan_schedule"
    ),

    

]