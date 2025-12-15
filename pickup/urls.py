from django.urls import path
from . import views

app_name = "pickups"

urlpatterns = [

    # =========================
    # Parent Side
    # =========================
    path(
        "parent/",
        views.parent_dashboard,
        name="parent_dashboard"
    ),

    path(
        "parent/generate/",
        views.create_pickup,
        name="generate_pickup"
    ),

    path(
        "parent/history/",
        views.pickup_history,
        name="pickup_history"
    ),

    # =========================
    # Admin / Security Side
    # =========================
    path(
        "admin/verify/",
        views.verify_pickup,
        name="verify_pickup"
    ),

    path(
        "admin/verify/<uuid:code>/",
        views.verify_pickup_detail,
        name="verify_pickup_detail"
    ),

    # path(
    #     "admin/verified/",
    #     views.verify_pickups,
    #     name="verified_pickups"
    # ),

    # =========================
    # QR Code Scan (JS / Camera)
    # =========================
    path(
        "scan/",
        views.qr_scan_page,
        name="qr_scan"
    ),

    path(
        "scan/lookup/",
        views.qr_lookup_api,
        name="qr_lookup_api"
    ),

    # =========================
    # API / Utilities
    # =========================
    path(
        "expire/",
        views.force_expire_pickup,
        name="force_expire_pickup"
    ),
]
