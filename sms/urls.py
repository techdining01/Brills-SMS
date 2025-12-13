# sms/urls.py
from django.urls import path, re_path
from . import views, consumers

app_name = 'sms'

urlpatterns = [
    # API endpoints
    # path('api/exam/start/<int:subject_id>/', views.StartExamView.as_view(), name='start_exam'),
    # path('api/exam/<int:session_id>/questions/', views.ExamQuestionsView.as_view(), name='exam_questions'),
    # path('exam/session/<int:session_id>/', views.exam_page, name='exam_page'),
    path('communication/', views.CommunicationCenterView.as_view(), name='communication_center'),
    re_path(r'ws/pta/chat/(?P<room_name>\w+)/$', consumers.PTAChatConsumer.as_asgi()),
    re_path(r'ws/pickup/scanner/$', consumers.PickupCodeConsumer.as_asgi()),
    
    path('communication/messages/', views.MessageCenterView.as_view(), name='message_center'),
    path('academics/resources/', views.ClassResourcesView.as_view(), name='class_resources'),
    path('academics/performance/', views.MyPerformanceView.as_view(), name='my_performance'),
   
    # --- Admin Change List Redirects ---
    path('manage/classes/', views.SchoolClassChangeListRedirectView.as_view(), name='manage_classes'),
 
    # Frontend views will go here later
    # path('exam/session/<int:session_id>/', views.exam_page, name='exam_page'),
]