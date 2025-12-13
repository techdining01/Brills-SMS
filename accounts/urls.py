from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import AdminDashboardView
from django.urls import reverse_lazy




app_name = 'accounts'


urlpatterns = [
    # 1. Registration Flow
    path('register/', views.role_select_view, name='role_select'),
    path('register/<str:role>/', views.register_view, name='register'),
    
    # 2. Authentication
    path('login/', views.CustomLoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', views.custom_logout_view, name='logout'),
    
    # 3. Dashboard Views
    path('dashboard/', AdminDashboardView.as_view(), name='admin_dashboard'),

    # 4. Parent Dashboard View 
    path('dashboard/parent/', views.ParentDashboardView.as_view(), name='parent_dashboard'), 
    
    # 5. Student Dashboard View
    path('dashboard/student/', views.StudentDashboardView.as_view(), name='student_dashboard'),

    path('account/settings/', views.SettingsProfileView.as_view(), name='settings_profile'),
    
   

]
        



