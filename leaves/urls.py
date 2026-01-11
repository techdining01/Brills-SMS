from django.urls import path
from . import views

app_name = "leaves"

urlpatterns = [
    path("", views.dashboard_router, name="home"),

    # Dashboards
    path("admin/", views.admin_dashboard, name="admin_dashboard"),
    path("staff/", views.staff_dashboard, name="staff_dashboard"),

    # Leave
    path("leave/calendar/", views.leave_calendar, name="leave_calendar"),
    path("leave/<int:pk>/approve/", views.approve_leave, name="approve_leave"),
    path("leave/<int:pk>/reject/", views.reject_leave, name="reject_leave"),

    path("reject/<int:leave_id>/", views.reject_leave, name="reject"),
]

urlpatterns += [
    path("ajax/<int:pk>/approve/", views.ajax_approve_leave, name="ajax_approve_leave"),
    path("ajax/<int:pk>/reject/", views.ajax_reject_leave, name="ajax_reject_leave"),
    path("history/", views.leave_history, name="leave_history"),
]
