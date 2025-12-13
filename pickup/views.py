from django.views.generic import TemplateView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from .models import PickupCode 
from .forms import PickupCodeGenerationForm 
from django.utils import timezone
from datetime import timedelta
from .utils import generate_qrcode
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model

# Ensure these imports are correct
from pickup.models import PickupCode # Your model for codes
from .utils import generate_qrcode # utility function for QR codes (as previously provided)



class ScannerView(UserPassesTestMixin, TemplateView):
    template_name = 'pickup/scanner.html'
    
    def test_func(self):
        # Only allow Admin and Staff/Teachers to access the scanner
        return self.request.user.is_authenticated and self.request.user.role in ['ADMIN', 'STAFF']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ws_url'] = f'ws://{self.request.get_host()}/ws/pickup/scanner/'
        return context


def is_parent(user):
    return user.is_authenticated and user.role == 'PARENT'


# @login_required
# def generate_pickup_code(request):
#     # Only Parents can generate codes
#     if request.user.role != 'PARENT':
#         messages.error(request, "Access denied. Only Parents can generate pickup codes.")
#         return redirect('home')

#     active_code = PickupCode.objects.filter(
#         parent=request.user,
#         is_verified=False,
#         expires_at__gt=timezone.now()
#     ).order_by('-generated_at').first()

#     qrcode_base64 = None
    
#     # --- Generation Logic ---
#     if request.method == 'POST':
#         # 1. Check for existing active code
#         if active_code:
#             messages.info(request, "An active code already exists. Please use the current one or wait for it to expire.")
#             return redirect('pickup:generate_pickup_code')

#         # 2. Check for linked students (crucial integrity check)
#         children = request.user.children.all()
#         if not children.exists():
#             messages.error(request, "You are not linked to any students. Cannot generate code.")
#             return redirect('sms:parent_dashboard')
        
#         # 3. Create the new code (using the first linked child for simplicity)
#         try:
#             new_code = PickupCode.objects.create(
#                 parent=request.user,
#                 student=children.first(), # Link to the first child
#                 expires_at=timezone.now() + timedelta(minutes=10) # 10 minute validity
#             )
#             active_code = new_code
#             messages.success(request, f"New pickup code generated: {new_code.code}")
            
#         except Exception as e:
#             messages.error(request, f"Failed to generate code: {e}")
#             return redirect('pickup:generate_pickup_code')

#     # --- Post-generation/Display Logic ---
#     if active_code:
#         # Generate the QR code image string
#         qrcode_base64 = generate_qrcode(active_code.code)

#     context = {
#         'active_code': active_code,
#         'qrcode_base64': qrcode_base64, # Pass the base64 string
#     }
#     return render(request, 'pickup/generate_pickup_code.html', context)



User = get_user_model()

@login_required
def generate_pickup_code(request):
    # Enforce role restriction
    if request.user.role != User.Role.PARENT:
        messages.error(request, "Access denied. Only Parents can generate pickup codes.")
        return redirect('home')
        
    parent = request.user
    
    # 1. Get all linked children
    # We use the 'children' related name defined in accounts/models.py
    linked_students = parent.children.all()

    if not linked_students.exists():
        messages.error(request, "You are not linked to any students. Please contact school administration.")
        return render(request, 'pickup/generate_pickup_code.html', {'linked_students': [], 'error': True})

    active_codes_data = []
    
    # --- Check and handle POST request (Code Generation) ---
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        try:
            student_to_code = linked_students.get(id=student_id)
        except User.DoesNotExist:
            messages.error(request, "Invalid student selected.")
            return redirect('pickup:generate_pickup_code')

        # Check for existing active code for this specific student
        existing_code = PickupCode.objects.filter(
            parent=parent,
            student=student_to_code,
            is_used=False,
            expires_at__gt=timezone.now()
        ).first()

        if existing_code:
            messages.info(request, f"An active code for {student_to_code.first_name} already exists.")
        else:
            # Create a new code (10 minutes validity)
            new_code = PickupCode.objects.create(
                parent=parent,
                student=student_to_code,
                expires_at=timezone.now() + timedelta(minutes=10) 
            )
            messages.success(request, f"New code generated for {student_to_code.first_name}: {new_code.code}")
            return redirect('pickup:generate_pickup_code') # Redirect to GET to show the new code

    # --- Prepare Context Data for Display ---
    for student in linked_students:
        # Find the currently active code for this specific student
        active_code = PickupCode.objects.filter(
            parent=parent,
            student=student,
            is_verified=False,
            expires_at__gt=timezone.now()
        ).order_by('-generated_at').first()

        qrcode_base64 = None
        if active_code:
            # Generate QR Code image string
            qrcode_base64 = generate_qrcode(active_code.code)
            
        active_codes_data.append({
            'student': student,
            'active_code': active_code,
            'qrcode_base64': qrcode_base64,
        })

    context = {
        'active_codes_data': active_codes_data,
        'linked_students': linked_students, # For the dropdown/buttons
    }
    return render(request, 'pickup/generate_pickup_code.html', context)



class VerificationTerminalView(UserPassesTestMixin, TemplateView):
    template_name = 'sms/verification_terminal.html'

    def test_func(self):
        # Only Staff and Admin can access the verification terminal
        return self.request.user.is_authenticated and self.request.user.role in ['ADMIN', 'STAFF']
    