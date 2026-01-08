from . import views
from django.urls import path
from django.contrib.auth import views as auth_views

app_name = 'accounts'


urlpatterns = [

        # path("login/", auth_views.LoginView.as_view(
        #     template_name="accounts/login.html",
        #     redirect_authenticated_user=True
        # ), name="login"),
        # path("register/", views.register, name="register"),

        # path("logout/", auth_views.LogoutView.as_view(), name="logout"),

        path('login/', views.login_view, name='login'),

        path('register/', views.register_view, name='register'),

        path('logout/', views.logout_view, name='logout'),

        path('redirect/', views.dashboard_redirect, name='dashboard_redirect'),

        path('post-login/', views.post_login_router, name='post_login_router'),

        path("complete-profile/", views.complete_profile, name="complete_profile"),


        # Usersusers
        path("users/", views.admin_users_management, name="users"),
        path("users/approve/", views.bulk_approve_users, name="bulk_approve"),
        path('pending-approval/', views.pending_approval, name='pending_approval'),
        path('admin/approve-users/', views.approve_users, name='approve_users'),
        path('admin/reset-password/<int:user_id>/', views.admin_reset_password, name='admin_reset_password'),
        path('create/admin_create_user', views.admin_create_user, name='admin_create_user'),
       
        #######################################################################

       
    ]