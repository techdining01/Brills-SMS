"""
URL configuration for school_sms project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from .views import landing_page, admin_grand_dashboard, about_page
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', landing_page, name='landing_page'),
    path('about/', about_page, name= 'about'),
    path("admin/mega-dashboard/", admin_grand_dashboard, name="admin_grand_dashboard"),
    path('dashboard/', include('dashboards.urls')),
    path('admin/', admin.site.urls),
    path('auth/', include('accounts.urls')), 
    path('brillspay/', include('brillspay.urls')),
    path('pickup/', include('pickup.urls')),
    path('payroll/', include('payroll.urls')),
    path('loans/', include('loans.urls')),
    path('leaves/', include('leaves.urls')),
    # path('sms/', include('sms.urls')),
    # path('management/', include('management.urls')),
]
# Serve media and static files locally when DEBUG=False
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


