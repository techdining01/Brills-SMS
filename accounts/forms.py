from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User
from django import forms    
    


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + (
            'email', 
            'first_name', 
            'last_name', 
            'phone_number', 
            'address'
        )
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure 'email' field is required
        self.fields['email'].required = True

    def save(self, commit=True):
        # 1. Call parent save method
        user = super().save(commit=False)
        
        # 2. Set role based on common initial use (Student)
        # For a self-registration portal, we default to PARENT or STUDENT.
        # Let's default all self-registered users to PARENT, as Student accounts
        # should typically be created by an Admin/Staff member for control.
        user.role = User.Role.PARENT
        
        if commit:
            user.save()
        return user

class CustomAuthenticationForm(AuthenticationForm):
    """Simple customization of the standard login form if needed."""
    pass

CustomAuthenticationForm()


class StudentForm(forms.ModelForm):
    # Remove the role field definition here entirely. 
    # The field is inherited from User, and we want to control its value.
    
    class Meta:
        model = User
        exclude = ('is_superuser', 'groups', 'user_permissions', 'date_joined', 'password')
        
        # Ensure 'role' is NOT in this fields list.
        fields = (
            'username', 'email', 'first_name', 'last_name', 
            'phone_number', 'address', 'student_class', 
            'parents', 
        )

    # Add the required fields for the base User model that are not in the form.
    # We must ensure the role is correctly set when the form data is mapped to the User instance.
    def clean(self):
        cleaned_data = super().clean()
        # Ensure the role is set for the base User model during validation
        if 'role' not in cleaned_data:
             cleaned_data['role'] = User.Role.STUDENT
        return cleaned_data
        
    def save(self, commit=True):
        # Set the role directly on the instance before saving
        instance = super().save(commit=False)
        instance.role = User.Role.STUDENT # <--- Crucial step for proxy models
        if commit:
            instance.save()
        return instance# accounts/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from sms.models import SchoolClass # Assuming SchoolClass is here

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    """Base form for all new user registrations."""
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'profile_picture')
        # Ensure 'role', 'is_approved' are NOT in fields, as they are set in the view/model.
        
    def save(self, commit=True):
        user = super().save(commit=False)
        # CRITICAL: Set user to inactive and unapproved by default
        user.is_active = False  
        user.is_approved = False
        if commit:
            user.save()
        return user

# --- Role-Specific Forms (for extra data) ---

class StudentRegistrationForm(CustomUserCreationForm):
    # Field to select the class, required for students
    student_class = forms.ModelChoiceField(
        queryset=SchoolClass.objects.all(),
        required=True,
        empty_label="Select Academic Class",
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded-lg focus:ring-blue-500 focus:border-blue-500'})
    )
    
    class Meta(CustomUserCreationForm.Meta):
        # Add student_class to the fields list
        fields = CustomUserCreationForm.Meta.fields + ('student_class',)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.STUDENT
        user.student_class = self.cleaned_data.get('student_class')
        if commit:
            user.save()
        return user

class ParentRegistrationForm(CustomUserCreationForm):
    class Meta(CustomUserCreationForm.Meta):
        pass # No extra fields needed, uses base fields

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.PARENT
        if commit:
            user.save()
        return user

class StaffRegistrationForm(CustomUserCreationForm):
    class Meta(CustomUserCreationForm.Meta):
        pass # No extra fields needed

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.STAFF
        if commit:
            user.save()
        return user