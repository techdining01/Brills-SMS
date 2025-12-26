

from django.urls import path
from . import views
from . import admin_views
from django.urls import path



app_name = "brillspay"

urlpatterns = [
    path("", views.store_view, name="store"),
    path("select-ward/", views.select_ward, name="brillspay_select_ward"),
    path("products/", views.product_list, name="brillspay_products"),
    path("cart/add/", views.add_to_cart, name="brillspay_add_to_cart"),
    path("cart/<int:ward_id>/", views.cart_view, name="brillspay_cart"),
    path("cart/sidebar/", views.cart_sidebar, name="brillspay_cart_sidebar"),
    path("cart/update/", views.update_cart_item, name="brillspay_update_cart_item"),
    path("cart/count/", views.cart_count, name="brillspay_cart_count"),
    path("checkout/", views.checkout, name="checkout"),
    path("checkout/<uuid:order_id>/", views.checkout_detail, name="checkout_detail"),

    path("receipt/<int:tx_id>/pdf/", views.payment_receipt_pdf, name="receipt_pdf"),
    # =======================
    # ADMIN DASHBOARD
    # =======================

    path("admin/dashboard/", admin_views.admin_dashboard, name="admin_dashboard"),

    # =======================
    # PRODUCTS & STOCK
    # =======================

    path("admin/orders/", admin_views.admin_order_list, name="admin_orders"),
    path("admin/orders/<uuid:pk>/", admin_views.admin_order_detail, name="admin_order_detail"),
    path("admin/products/add/", admin_views.admin_add_product, name="admin_add_product"),
    path("admin/products/<int:pk>/edit/", admin_views.admin_edit_product, name="admin_edit_product"),
    path("admin/products/<int:pk>/delete/", admin_views.admin_delete_product, name="admin_delete_product"),

    # Stock control
    path("admin/products/<int:pk>/stock/add/", admin_views.admin_add_stock, name="admin_add_stock"),
    path("admin/products/<int:pk>/stock/remove/", admin_views.admin_remove_stock, name="admin_remove_stock"),

    # =======================
    # ORDERS & PAYMENTS
    # =======================
    path("admin/orders/", admin_views.admin_order_list, name="admin_order_list"),
    path("admin/orders/<int:pk>/", admin_views.admin_order_detail, name="admin_order_detail"),

    path("admin/payments/", admin_views.admin_payment_list, name="admin_payment_list"),
    path("admin/payments/<int:pk>/", admin_views.admin_payment_detail, name="admin_payment_detail"),

    # =======================
    # ACCESS UNLOCKS
    # =======================
    path("admin/access/", admin_views.admin_access_list, name="admin_access_list"),
    
    path("admin/access/grant/<int:order_id>/", admin_views.admin_grant_access, name="admin_grant_access"),
    
    path("admin/access/revoke/<int:access_id>/", admin_views.admin_revoke_access, name="admin_revoke_access"),

    # =======================
    # TRANSACTION LOGS
    # =======================
    path("admin/transactions/", admin_views.admin_transaction_logs, name="admin_transaction_logs"),
    path("admin/analytics/", admin_views.admin_analytics_dashboard, name="admin_analytics"),

    # 👉 Paystack init
    path('paystack/init/<str:order_id>/', views.paystack_initialize, name='paystack_init'),
    
    # 👉 Paystack callback (redirect)
    path("paystack/callback/", views.paystack_callback, name="paystack_callback"),

    # 👉 Webhook (POST only, no CSRF)
    path("paystack/webhook/", views.paystack_webhook, name="paystack_webhook"),
    path("payment_status_check/", views.payment_status_check, name="payment_status_check"),
    path("admin/webhooks/", views.webhook_monitor, name="webhook_monitor"),





]




