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
    path('payment/webhook/', views.paystack_webhook, name='paystack_webhook'),
    # path('payment/callback/', views.payment_callback, name='payment_callback'),
    path('checkout/', views.checkout, name='checkout'),

]
