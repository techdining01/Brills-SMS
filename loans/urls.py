from django.urls import path
from . import views

app_name = "loans"

urlpatterns = [
    # Admin
    path("admin/dashboard/", views.admin_loan_dashboard, name="admin_loan_dashboard"),
    path("admin/<int:loan_id>/", views.admin_loan_detail, name="admin_loan_detail"),
    path("admin/<int:loan_id>/approve/", views.approve_loan, name="approve_loan"),
    path("admin/<int:loan_id>/reject/", views.reject_loan, name="reject_loan"),
    path("admin/export/", views.export_loans, name="export_loans"),

    # Staff
    path("dashboard/", views.staff_loan_dashboard, name="staff_loan_dashboard"),
    path("apply/", views.apply_for_loan, name="apply_loan"),
    path("my-loans/", views.loan_list, name="loan_list"),

]
