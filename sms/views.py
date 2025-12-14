from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import  Subject
# from .serializers import QuestionSerializer
# from .utils import start_cbt_session    # function to create session and randomize

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import TemplateView, RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import get_user_model


User = get_user_model()


class CommunicationCenterView(UserPassesTestMixin, TemplateView):
    template_name = 'sms/communication_center.html'
    
    def test_func(self):
        # Only allow Admin and Staff/Teachers to access the center
        return self.request.user.is_authenticated and self.request.user.role in ['ADMIN', 'STAFF']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass the WebSocket URL needed for this communication consumer
        context['ws_url'] = f'ws://{self.request.get_host()}/ws/broadcast/'
        return context
    

# --- Common Mixins ---
class ParentRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == User.Role.PARENT

class StudentRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == User.Role.STUDENT

# ----------------------------------------------------------------------
# 4. Class Resources (Student/Teacher Link)
# ----------------------------------------------------------------------
class ClassResourcesView(LoginRequiredMixin, TemplateView):
    template_name = 'feature_placeholders/class_resources.html'
    
    # Restrict to Students and Staff (who might upload/manage resources)
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and user.role in [User.Role.STUDENT, User.Role.STAFF]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Class Resources"
        # Logic to list PDFs, links, videos related to the student's class
        return context

# ----------------------------------------------------------------------
# 5. My Performance (Student Link)
# ----------------------------------------------------------------------
class MyPerformanceView(StudentRequiredMixin, TemplateView):
    template_name = 'feature_placeholders/my_performance.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Academic Performance"
        # Logic to fetch grades, exam history, charts, etc.
        return context
        
# ----------------------------------------------------------------------
# 3. Messages/Communication (Common Link - All authenticated users)
# ----------------------------------------------------------------------
class MessageCenterView(LoginRequiredMixin, TemplateView):
    template_name = 'feature_placeholders/message_center.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Internal Message Center"
        # Logic to fetch message threads, compose new messages, etc., would go here
        return context



# Helper Mixin to ensure only Admin/Staff can access these redirects
class AdminStaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role in [User.Role.ADMIN, User.Role.STAFF]


class SchoolClassChangeListRedirectView(AdminStaffRequiredMixin, RedirectView):
    """Redirects to the Django Admin Change List for SchoolClass."""
    permanent = False
    query_string = True
    # Assuming SchoolClass is in the 'sms' app
    pattern_name = 'sms:sms_schoolclass_changelist' 


     
class MessageCenterView(LoginRequiredMixin, TemplateView):
    template_name = 'feature_placeholders/message_center.html'

class ClassResourcesView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'feature_placeholders/class_resources.html'
    # Restrict to Students and Staff (who might upload/manage resources)
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and user.role in [User.Role.STUDENT, User.Role.STAFF]

class MyPerformanceView(StudentRequiredMixin, TemplateView):
    template_name = 'feature_placeholders/my_performance.html'
