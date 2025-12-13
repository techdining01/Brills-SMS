from django.urls import path
from django.shortcuts import render
from . import views


app_name = 'brillspay'

urlpatterns = [
    # The webhook endpoint. This URL should be configured in your Paystack dashboard.
    path('webhook/paystack/', views.paystack_webhook, name='paystack_webhook'),
]


urlpatterns += [
    # Storefront URLs
    path('', views.product_list, name='product_list'),
    path('<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    
    # Cart URLs
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/', views.cart_detail, name='cart_detail'),
    
    # Checkout URLs
    path('checkout/', views.checkout_create, name='checkout_create'),
    
    # --- New Feature Paths ---
    path('finance/billing/', views.BillingPaymentView.as_view(), name='billing_payments'),

    # Payment Verification (Placeholder)
    # This view would handle the redirect back from Paystack
    path('payment/verify/<int:order_id>/', lambda request, order_id: render(request, 'brillspay/payment_success.html', {'order_id': order_id}), name='payment_verify'),
    path('manage/products/', views.ProductChangeListRedirectView.as_view(), name='manage_products'),


    # --- BrillsPay Admin Views (NEW) ---
    path('admin/products/', views.admin_product_list, name='admin_product_list'),
    path('admin/products/create/', views.admin_product_create, name='admin_product_create'),
    path('admin/products/update/<int:pk>/', views.admin_product_update, name='admin_product_update'),
    path('admin/products/delete/<int:pk>/', views.admin_product_delete, name='admin_product_delete'),


]