from django.urls import path
from . import views

app_name = 'pickup'

urlpatterns = [
    # Staff/Admin Scanner Interface
    path('scanner/', views.ScannerView.as_view(), name='pickup_scanner'),
    path('pickup/generate/', views.generate_pickup_code, name='generate_pickup_code'),
    path('pickup/verify/', views.VerificationTerminalView.as_view(), name='verification_terminal'),


]