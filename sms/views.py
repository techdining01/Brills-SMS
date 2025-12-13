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






# class StartExamView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, subject_id):
#         """
#         Starts a new CBT session for the authenticated student.
#         """
#         user = request.user
#         if user.role != 'STUDENT':
#             return Response({'detail': 'Only students can start an exam.'}, 
#                             status=status.HTTP_403_FORBIDDEN)

#         subject = get_object_or_404(Subject, pk=subject_id)
        
#         # Check if the student already has an unsubmitted session for this subject
#         if CBTExamSession.objects.filter(student=user, subject=subject, is_submitted=False).exists():
#             return Response({'detail': 'Unsubmitted session already exists. Retrieve it instead.'}, 
#                             status=status.HTTP_400_BAD_REQUEST)
        
#         try:
#             # Calls our utility function to create session and randomize data
#             session = start_cbt_session(student=user, subject=subject)
            
#             return Response({
#                 'session_id': session.id,
#                 'message': f'Exam session started for {subject.name}'
#             }, status=status.HTTP_201_CREATED)
            
#         except ValueError as e:
#             return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# class ExamQuestionsView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, session_id):
#         """
#         Retrieves the randomized questions for a specific exam session.
#         """
#         # Ensure the session belongs to the authenticated user
#         session = get_object_or_404(
#             CBTExamSession, 
#             pk=session_id, 
#             student=request.user, 
#             is_submitted=False
#         )

#         # 1. Get the list of question IDs from the randomized session data
#         question_ids = [q['question_id'] for q in session.question_order_data['questions']]
        
#         # 2. Fetch the actual Question objects in the randomized order
#         # (This uses Python list comprehension, not a DB order_by, which is fine for short lists)
#         questions = CBTQuestion.objects.filter(id__in=question_ids)
#         question_map = {q.id: q for q in questions}
        
#         ordered_questions = [question_map[id] for id in question_ids]

#         # 3. Pass the critical session data to the serializer's context
#         # This is how the serializer gets the randomization map!
#         context = {
#             'session_data': session.question_order_data,
#             'request': request
#         }
        
#         serializer = QuestionSerializer(ordered_questions, many=True, context=context)
        
#         return Response({
#             'session_id': session.id,
#             'questions': serializer.data,
#             # We'll add the heartbeat endpoint here for the frontend later
#         })
    

# @login_required
# def exam_page(request, session_id):
#     """
#     Renders the main exam page. The JavaScript will handle data fetching.
#     """
#     session = get_object_or_404(
#         CBTExamSession, 
#         pk=session_id, 
#         student=request.user, 
#         is_submitted=False
#     )
    
#     context = {
#         'session_id': session_id,
#         # Pass the WebSocket URL needed for the heartbeat
#         'ws_url': f'ws://{request.get_host()}/ws/exam/{session_id}/'
#     }
#     return render(request, 'sms/exam_page.html', context)


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