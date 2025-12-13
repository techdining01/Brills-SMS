from django.urls import path
from . import views

app_name = 'management'

urlpatterns = [
    path('data/', views.backup_restore_view, name='backup_restore'),
]