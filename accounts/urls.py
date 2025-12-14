from django.urls import path
from . import views

app_name = 'accounts'


urlpatterns = [
path('login/', views.login_view, name='login'),
path('logout/', views.logout_view, name='logout'),
path('redirect/', views.dashboard_redirect, name='dashboard_redirect'),


path('admin/create-student/', views.create_student, name='create_student'),
path('admin/approve-users/', views.approve_users, name='approve_users'),
path('admin/reset-password/<int:user_id>/', views.admin_reset_password, name='admin_reset_password'),

]