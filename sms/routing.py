
from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    # 1. CBT Exam Monitoring (for student heartbeats)
    re_path(r'ws/exam/(?P<session_id>\w+)/$', consumers.ExamMonitorConsumer.as_asgi()),
    
    # 2. General Communication (The new requirement)
    # A single endpoint to handle both staff-staff chat and staff-student broadcast
    re_path(r'ws/broadcast/$', consumers.CommunicationConsumer.as_asgi()),
]