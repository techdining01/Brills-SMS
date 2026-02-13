import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path, re_path
from dashboards.routing import websocket_urlpatterns

# Ensure this import path is correct for your consumer
# from sms.consumers import PickupCodeConsumer 

# IMPORTANT: Replace 'school_sms' with your project config folder name!
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_sms.settings')

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": get_asgi_application(), 
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns, 
       )
    ),
})

