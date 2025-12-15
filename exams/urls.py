from django.urls import path 
from . import views

# app_name = 'exams'

urlpatterns = [
   
    # exams/urls.py
    path('student/exams/', views.exam_list, name='exam_list'),
    path('student/exams/<int:exam_id>/start/', views.start_exam, name='start_exam'),
    path('student/exams/<int:attempt_id>/resume/', views.resume_exam, name='resume_exam'),
    path('student/exams/<int:attempt_id>/submit/', views.submit_exam, name='submit_exam'),
    
    path('teacher/exams/create/', views.create_exam, name='create_exam'),
    path('teacher/exams/', views.teacher_exam_list, name='teacher_exam_list'),
    path('teacher/exams/<int:exam_id>/questions/', views.question_list, name='question_list'),
    path('teacher/exams/<int:exam_id>/questions/add/', views.add_question, name='add_question'),
    path('teacher/exams/<int:exam_id>/questions/upload-excel/',views.upload_questions_excel, name='upload_questions_excel'),
    path('teacher/exams/<int:exam_id>/questions/upload-word/', views.upload_questions_word, name='upload_questions_word'),
    # Teacher subjective marking
    path('teacher/exams/<int:exam_id>/mark/', views.subjective_marking, name='subjective_marking'),

    # Student dashboard (view their own results)
    path('student/results/', views.student_results, name='student_results'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('parent/dashboard/', views.parent_dashboard, name='parent_dashboard'),

    
    # Class leaderboard
    path('teacher/classes/<int:class_id>/leaderboard/', views.class_leaderboard, name='class_leaderboard'),

    path('teacher/grade/', views.teacher_grading_dashboard, name='teacher_grading_dashboard'),
    path('teacher/grade/save/<int:answer_id>/', views.save_subjective_mark, name='save_subjective_mark'),
    
    # Retake
    path('student/exams/<int:exam_id>/retake/', views.request_retake, name='request_retake'),
    path('admin/retakes/', views.manage_retake, name='manage_retake'),

    # Notifications
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('notifications/mark-read/<int:pk>/', views.mark_notification_read, name='mark_notification_read'),

    # Broadcast
    path('teacher/broadcast/', views.send_broadcast, name='send_broadcast'),

    # exams/urls.py
    path('admin/exams/', views.admin_exam_list, name='admin_exam_list'),
    path('admin/exams/<int:pk>/toggle/', views.toggle_exam_publish, name='toggle_exam_publish'),


]