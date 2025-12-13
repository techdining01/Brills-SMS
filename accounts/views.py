from django.contrib.auth.views import LoginView
from django.views.generic import CreateView
from .forms import StudentRegistrationForm, ParentRegistrationForm, StaffRegistrationForm, CustomAuthenticationForm
from .models import User
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from sms import utils # Import our new utilities file
from django.utils import timezone
from django.contrib.auth.decorators import user_passes_test
# Assuming your models are imported correctly
from pickup.models import PickupCode 
from brillspay.models import Transaction 
from django.views.generic import RedirectView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views.generic import TemplateView
from django.contrib.auth import get_user_model



User = get_user_model()


# --- Common Mixins ---
class ParentRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == User.Role.PARENT

class StudentRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == User.Role.STUDENT


# --- 1. Custom Registration Views ---
def role_select_view(request):
    """Initial view to select the role before registration."""
    if request.user.is_authenticated:
        return redirect('home')
        
    return render(request, 'role_select.html', {'roles': User.Role.choices})

def register_view(request, role):
    """Handles the actual registration form submission."""
    # Ensure the role is valid
    role_map = {
        'student': {'form': StudentRegistrationForm, 'role_name': User.Role.STUDENT.label},
        'parent': {'form': ParentRegistrationForm, 'role_name': User.Role.PARENT.label},
        'staff': {'form': StaffRegistrationForm, 'role_name': User.Role.STAFF.label},
    }

    if role not in role_map:
        messages.error(request, "Invalid role selected.")
        return redirect('accounts:role_select')

    FormClass = role_map[role]['form']
    role_name = role_map[role]['role_name']

    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            
            # The user is created but is NOT active/approved.
            # We don't log them in, we inform them of the approval process.
            
            messages.success(request, 
                f"Successfully registered as a {role_name}. Your account is pending admin approval. You will receive an email once approved."
            )
            return redirect('accounts:login') # Redirect to login page
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = FormClass()
        
    context = {
        'form': form,
        'selected_role': role_name,
        'role_key': role,
    }
    return render(request, 'accounts/register.html', context)


# --- 2. Custom Login View (for Role-Based Redirection) ---
class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = CustomAuthenticationForm

    def get_success_url(self):
        # Logic to redirect based on user role after successful login
        user = self.request.user
        
        if user.role == User.Role.STUDENT:
            # Students go to their dashboard
            return reverse_lazy('accounts:student_dashboard')
        elif user.role == User.Role.PARENT:
            # Parents typically see their children's dashboard/PTA access
            return reverse_lazy('accounts:parent_dashboard') # To be implemented later
        elif user.role in [User.Role.ADMIN, User.Role.STAFF]:
            # Admin/Staff can go to a dedicated admin portal or the general admin site
            return reverse_lazy('accounts:admin_dashboard') 
        else:
            return reverse_lazy('accounts:login')

# --- 3. Logout View ---
def custom_logout_view(request):
    logout(request)
    return redirect(reverse_lazy('accounts:login'))


# Import proxy models
from accounts.models import Student, Parent, Staff 

User = get_user_model()

class AdminDashboardView(UserPassesTestMixin, TemplateView):
    template_name = 'accounts/admin_dashboard.html'
    
    def test_func(self):
        # Only allow authenticated Admin or Staff users
        return self.request.user.is_authenticated and self.request.user.role in [User.Role.ADMIN, User.Role.STAFF]
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # --- Critical: Approval Count ---
        context['unapproved_users'] = User.objects.filter(is_approved=False, is_superuser=False)
        
        # --- Module Counts ---
        context['student_count'] = Student.objects.count()
        context['parent_count'] = Parent.objects.count()
        context['staff_count'] = Staff.objects.count()
        
        # Add more counts here (e.g., pending transactions, total classes)
        
        return context
    

class StudentDashboardView(UserPassesTestMixin, TemplateView):
    template_name = 'accounts/student_dashboard.html'

    def test_func(self):
        # Allow STUDENTS to view their dashboard. 
        # For parents, we'd check if they are related to a student in the URL, 
        # but for simplicity now, we check the user role.
        return self.request.user.is_authenticated and self.request.user.role == 'STUDENT'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Fetch the performance data from our utility function
        performance_data = utils.get_student_performance_data(user.id)
        
        # The data is already JSON-dumped in the utility function, 
        # making it safe to pass directly to JavaScript.
        context.update(performance_data)
        context['student_name'] = user.get_full_name() or user.username
        
        return context
    


class ParentDashboardView(UserPassesTestMixin, TemplateView):
    template_name = 'accounts/parent_dashboard.html'

    def test_func(self):
        # Only allow authenticated PARENT users to view this dashboard
        return self.request.user.is_authenticated and self.request.user.role == 'PARENT'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # --- Basic Information ---
        context['parent_name'] = user.get_full_name() or user.username
        
        # --- 1. Students linked to this parent ---
        # Access students through the 'children' related name defined in the User model
        linked_students = user.children.all()
        context['linked_students'] = linked_students
        context['student_count'] = linked_students.count()

        # --- 2. Latest Pickup Code Status ---
        # Find the latest active code for display on the dashboard card
        latest_code = PickupCode.objects.filter(
            parent=user,
            is_verified=False,
            expires_at__gt=timezone.now()
        ).order_by('-generated_at').first()
        
        context['latest_pickup_code'] = latest_code

        # --- 3. Billing/Payment status (Recent Transactions) ---
        # Fetch the last 5 transactions made by this parent
        recent_transactions = Transaction.objects.filter(
            user=user
        ).order_by('-created_at')[:5]
        
        context['recent_transactions'] = recent_transactions
        
        # --- In the future, you would query for: ---
        # 4. Academic Performance Snapshots (from linked_students)
        # 5. Fee balances (if a dedicated Fee model existed)
        
        return context


@login_required
def home_redirect_view(request):
    """Redirects authenticated users to their appropriate dashboard."""
    if not request.user.is_approved:
        messages.warning(request, "Your account is pending approval. Please wait for an administrator to activate your account.")
        return redirect('accounts:login')
        
    if request.user.role in [User.Role.ADMIN, User.Role.STAFF]:
        return redirect('accounts:admin_dashboard')
    elif request.user.role == User.Role.PARENT:
        return redirect('accounts:parent_dashboard') # Assuming you have this view/URL name
    elif request.user.role == User.Role.STUDENT:
        return redirect('accounts:student_dashboard') # Assuming you have this view/URL name
        
    return redirect('accounts:logout') # Default safety measure


# If SchoolClass is in the accounts app, use:
# pattern_name = 'admin:accounts_schoolclass_changelist' 
# (Based on previous context, I will stick to 'sms' for SchoolClass)




class SettingsProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'feature_placeholders/settings_profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Account Settings & Profile"
        # Logic for profile forms, password change, etc., would go here
        return context
    
