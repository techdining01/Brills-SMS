import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path, re_path
from dashboards.routing import consumers


# Ensure this import path is correct for your consumer
# from sms.consumers import PickupCodeConsumer 

# IMPORTANT: Replace 'school_sms' with your project config folder name!
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_sms.settings')

django_asgi_app = get_asgi_application()


websocket_urlpatterns = [
    # path('ws/pickup/', PickupCodeConsumer.as_asgi()), 
]

websocket_urlpatterns += [
    re_path(r'ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
    re_path(r'ws/grading-notifications/$', consumers.GradingNotificationConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    "http": get_asgi_application(), 
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns, 
       )
    ),
})

