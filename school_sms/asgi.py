import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path

# Ensure this import path is correct for your consumer
from sms.consumers import PickupCodeConsumer 

# IMPORTANT: Replace 'school_sms' with your project config folder name!
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_sms.settings')

websocket_urlpatterns = [
    path('ws/pickup/', PickupCodeConsumer.as_asgi()), 
]

application = ProtocolTypeRouter({
    "http": get_asgi_application(), 
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})