from django.urls import path 
from . import views

app_name = 'exams'

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
    # path('teacher/exams/<int:exam_id>/mark/', views.subjective_marking, name='subjective_marking'),

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
    path("admin/exams/retake/<int:exam_id>/", views.admin_toggle_retake, name="admin_toggle_retake"),
    path('admin/pta-requests/', views.pta_request_list, name='pta_request_list'),
    path("analytics/", views.admin_analytics_dashboard, name="analytics"),

    
    # Admin Dashboard
    path("", views.cbt_exam, name="exams"),
    path("admin/dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("system-logs/", views.system_logs, name="system_logs"),
    path("grant-exam-access/", views.grant_exam_access, name="grant_exam_access"),


    path("admin/exam-access/", views.admin_exam_access, name="admin_exam_access"),
    path("admin/attempts/<int:exam_id>/", views.admin_exam_attempts, name="admin_exam_attempts"),
    path("admin/attempts/reset/<int:attempt_id>/", views.admin_reset_attempt, name="admin_reset_attempt"),
    path("exam/autosave/", views.autosave_answer, name="autosave_answer"),
    path("student/exam/<int:attempt_id>/", views.save_exam_progress, name="save_exam_progress"),
    path("student/exam/<int:attempt_id>/submit/", views.submit_exam, name="submit_exam"),
    path("student/leaderboard/<int:exam_id>/", views.student_leaderboard, name="student_leaderboard"),


    path("result/<int:attempt_id>/pdf/", views.export_result_pdf, name="export_result_pdf"),
    path("verify/<int:attempt_id>/<uuid:token>/", views.verify_result, name="verify_result"),
    path("admin/exam/<int:exam_id>/results/pdf/", views.admin_bulk_exam_results_pdf, name="admin_bulk_exam_results_pdf"),
    path("teacher/exam/<int:exam_id>/grading/pdf/", views.teacher_grading_summary_pdf, name="teacher_grading_summary_pdf"),


]



