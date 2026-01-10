from django.urls import path
from . import views
from django.urls import path


app_name = "payroll"

urlpatterns = [
    path("dashboard/", views.payroll_dashboard, name="dashboard"),

    # Admin
    # path("admin/", views.admin_dashboard, name="admin_dashboard"),

    path("admin/records/", views.payroll_record_list, name="payroll_record_list"),
    path("admin/records/<int:pk>/", views.payroll_record_detail, name="payroll_record_detail"),

    path("admin/payees/", views.payee_list, name="payee_list"),

    path("admin/payees/<int:pk>/", views.payee_detail, name="payee_detail"),

    # Payment batch
    path("admin/period/<int:period_id>/create-batch/", views.create_payment_batch_view, name="create_payment_batch",),
    path("admin/batch/<int:batch_id>/", views.payment_batch_detail, name="batch_detail",),
    
    # Paystack
    path("admin/batch/<int:batch_id>/execute/", views.execute_payment_batch, name="execute_batch",),
    path("admin/batch/<int:batch_id>/retry_failed/", views.retry_failed_transactions, name="retry_failed_transactions"),

    path("admin/audit-logs/", views.audit_log_list, name="audit_log_list"),

    # Payroll Period
    path("periods/", views.payroll_period_list, name="payroll_period_list"),
    
    path("periods/create/", views.create_payroll_period, name="create_payroll_period",),

    path("periods/<int:period_id>/", views.payroll_period_detail, name="payroll_period_detail",),

    path("periods/<int:period_id>/approve/", views.approve_payroll_period, name="approve_payroll_period"),

    path("period/<int:period_id>/lock/", views.lock_payroll_period, name="lock_period"),

    # Payroll generation
    path("period/<int:period_id>/generate/", views.generate_payroll_for_period, name="generate_payroll_for_period"),

    # Approvals
    path("record/<int:record_id>/approve/bursar/", views.bursar_approve_payroll, name="bursar_approve"),

    path("record/<int:record_id>/approve/admin/", views.admin_approve_payroll, name="admin_approve"),

    path("enroll/<int:user_id>/", views.enroll_user_to_payroll, name="enroll"),

   
    # Payment Batch
    path("batch/<int:batch_id>/", views.payment_batch_detail, name="batch_detail"),
    path("period/<int:period_id>/create_batch/", views.create_payment_batch_view, name="create_payment_batch"),
    path("batch/<int:batch_id>/execute/", views.execute_payment_batch, name="execute_payment_batch"),


]



urlpatterns += [
    
    path("staff/salary/history/", views.staff_salary_history, name="salary_history"),
    path("staff/salary/payslip/<int:payroll_id>/pdf/", views.payslip_pdf_view, name="payslip_pdf"),
    path("staff/salary/<int:pk>/", views.salary_detail, name="salary_detail"),
    # path("staff/payroll/dashboard/", views.staff_payroll_dashboard, name="staff_payroll_dashboard"),
    # path("admin/payroll/dashboard/", views.admin_payroll_dashboard, name="admin_payroll_dashboard"),
    # path("batches/<int:batch_id>/", views.payment_batch_detail, name="payment_batch_detail"),
    # path("retry/<int:tx_id>/", views.retry_payment, name="retry_payment"),
    # path("admin/payroll/<int:period_id>/generate/", views.generate_payroll_view, name="generate_payroll"),
   

    path("payroll/chart/", views.payroll_chart_data, name="payroll_chart_data"),
    path("staff/charts/salary/", views.staff_salary_chart, name="staff_salary_chart"),
    path("charts/monthly-payroll/", views.monthly_payroll_chart, name="monthly_payroll_chart"),
    

    # path("admin/staff/loan-payroll/dashboard/", views.staff_loan_payroll_dashboard, name="staff_loan_payroll_dashboard"),
    # path("admin/admin/loan-payroll/dashboard", views.admin_loan_payroll_dashboard, name="admin_loan_payroll_dashboard"),





]



# urlpatterns += [

#     # =========================
#     # STAFF SELF-SERVICE
#     # =========================
#     path(
#         "dashboard/",
#         views.staff_dashboard,
#         name="staff_dashboard"
#     ),

#     path(
#         "payslips/",
#         views.staff_payslip_list,
#         name="staff_payslips"
#     ),

#     path(
#         "payslip/<int:payroll_id>/pdf/",
#         views.download_payslip_pdf,
#         name="download_payslip_pdf"
#     ),

#     path(
#         "loans/",
#         views.staff_loan_dashboard,
#         name="staff_loans"
#     ),

#     path(
#         "loan/request/",
#         views.request_loan,
#         name="request_loan"
#     ),

#     # =========================
#     # ADMIN / BURSAR – PAYROLL
#     # =========================
 
#     path(
#         "admin/payroll/run/",
#         views.run_payroll,
#         name="run_payroll"
#     ),

#     path(
#         "admin/payroll/<int:payroll_id>/approve/",
#         views.approve_payroll,
#         name="approve_payroll"
#     ),

#     path(
#         "admin/payroll/<int:payroll_id>/pay/",
#         views.pay_payroll,
#         name="pay_payroll"
#     ),

#     path(
#         "admin/payroll/<int:payroll_id>/resend-payslip/",
#         views.resend_payslip,
#         name="resend_payslip"
#     ),

   
#     # =========================
#     # ADMIN – AUDIT LOGS
#     # =========================
#     path(
#         "admin/audit-logs/",
#         views.audit_logs,
#         name="audit_logs"
#     ),

# ]
