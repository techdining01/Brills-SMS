

from django.urls import path
from . import views
from .admin_views import admin_orders, admin_order_detail

app_name = "brillspay"

urlpatterns = [
    path("", views.store, name="store"),
    path("cart/", views.cart_view, name="cart"),
    path("cart/add/", views.add_to_cart, name="add_to_cart"),
    path("cart/remove/", views.remove_from_cart, name="remove_from_cart"),
    path("checkout/", views.checkout_view, name="checkout"),
    path("checkout/", views.checkout_view, name="checkout"),
    path("payment/callback/", views.payment_callback, name="payment_callback"),
    path("webhook/paystack/", views.paystack_webhook, name="paystack_webhook"),


    path("admin/orders/", admin_orders, name="admin_orders"),
    path("admin/orders/<uuid:pk>/", admin_order_detail, name="admin_order_detail"),


]
