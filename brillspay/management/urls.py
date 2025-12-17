from django.urls import path
from django.shortcuts import render
from . import views


app_name = 'brillspay'

urlpatterns = [
    # The webhook endpoint. This URL should be configured in your Paystack dashboard.
    # path('webhook/paystack/', views.paystack_webhook, name='paystack_webhook'),
]


urlpatterns += [
    path('', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path("cart/update/", views.update_cart, name="update_cart"),
    path("cart/remove/", views.remove_from_cart, name="remove_from_cart"),
    path('checkout/', views.checkout_view, name='checkout'),
    path("paystack/init/", views.init_paystack_payment, name="init_payment"),
    # path("payment/callback/", views.payment_callback, name="payment_callback"),
    path('payment/webhook/', views.paystack_webhook, name='paystack_webhook'),

    # Order management for admins
    path("admin/orders/", views.admin_orders, name="admin_orders"),
    path("admin/orders/<int:order_id>/", views.admin_order_detail, name="admin_order_detail"),
    path("admin/products/stock/<int:product_id>/", views.admin_update_stock, name="admin_update_stock"),

]
