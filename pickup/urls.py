from django.urls import path
from . import views

app_name = "pickups"

urlpatterns = [

    # =========================
    # Parent Side
    # =========================
    path("parent/", views.parent_dashboard, name="parent_dashboard"),

    path("parent/generate/", views.generate_pickup_code, name="generate_pickup"),

    path("pickup/parent/history/", views.parent_pickup_history, name="parent_pickup_history"),

    # path("parent/history/", views.pickup_history, name="pickup_history"),

    # =========================
    # Admin / Security Side
    # =========================

    path("admin/dashboard/", views.pickup_admin_dashboard, name="admin_dashboard"),

    path("admin/verify/<str:reference>/", views.verify_pickup, name="verify_pickup"),

    path("admin/verify/detail/<str:reference>/", views.verify_pickup_detail, name="verify_pickup_detail"),

    path("admin/force-expire/<int:pickup_id>/", views.force_expire_pickup, name="force_expire_pickup"),

    path("admin/scan/", views.pickup_scan, name="pickup_scan"),

    path("pickup/admin/audit/pdf/", views.pickup_audit_log_pdf, name="pickup_audit_log_pdf"),

    path("pickup/admin/daily-report/pdf/", views.daily_pickup_report_pdf, name="daily_pickup_report_pdf"),

    # path("admin/verified/", views.verify_pickups, name="verified_pickups"),

   
    # =========================
    # API / Utilities
    # =========================

    path("pickup/admin/force-expire/<int:pickup_id>/", views.force_expire_pickup, name="force_expire_pickup")


]