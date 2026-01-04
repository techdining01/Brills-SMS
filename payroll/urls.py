from django.urls import path
from . import views


app_name = 'payroll'


urlpatterns = [
    
    path("staff/salary/history/", views.staff_salary_history, name="salary_history"),
    path("staff/salary/payslip/<int:payroll_id>/pdf/", views.payslip_pdf_view, name="payslip_pdf"),
    path("staff/leave/apply/", views.staff_apply_leave, name="staff_apply_leave"),
    path("staff/leave/history/", views.staff_leave_history, name="staff_leave_history"),
    path("staff/payroll/dashboard/", views.staff_payroll_dashboard, name="staff_payroll_dashboard"),
    path("admin/payroll/dashboard/", views.admin_payroll_dashboard, name="admin_payroll_dashboard"),
    path("charts/monthly-payroll/", views.monthly_payroll_chart, name="monthly_payroll_chart"),
    path("batches/<int:batch_id>/", views.payment_batch_detail, name="payment_batch_detail"),
    path("retry/<int:tx_id>/", views.retry_payment, name="retry_payment"),
    path("admin/payroll/<int:period_id>/generate/", views.generate_payroll_view, name="generate_payroll"),


]


