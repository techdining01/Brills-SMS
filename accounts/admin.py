from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Student


# Define fieldsets for non-Student roles (Admin/Staff/Parent)
STAFF_USER_FIELDSETS = (
    (None, {'fields': ('username', 'password')}),
    ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'address')}),
    ('Role and Status', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser')}),
    ('Permissions', {'fields': ('groups', 'user_permissions')}),
    ('Important dates', {'fields': ('last_login', 'date_joined')}),
)

# Define fieldsets for Student role
STUDENT_USER_FIELDSETS = (
    (None, {'fields': ('username', 'password')}),
    ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'address')}),
    ('Academic Details', {'fields': ('student_class', 'admission_number', 'parent')}), # student_class is HERE
    ('Status', {'fields': ('is_active',)}),
    ('Emergency Contact', {'fields': ('emergency_contact', 'emergency_phone')}),
)


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from .forms import CustomUserCreationForm # Use the base creation form

User = get_user_model()

# Custom Action for Admin Approval
@admin.action(description='Approve selected users')
def approve_users(modeladmin, request, queryset):
    # Set is_approved and also set is_active to True, as they can now log in
    queryset.update(is_approved=True, is_active=True)

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm # Use the custom form for creating users in the admin
    
    # Custom fields for display on the change list page
    list_display = (
        'username', 
        'email', 
        'first_name', 
        'role', 
        'is_approved', # CRITICAL: Show approval status
        'is_active', 
        'is_staff'
    )
    
    # Fields to show when editing a user
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'profile_picture', 'phone_number', 'address')}),
        ('School Role', {'fields': ('role', 'student_class', 'parents')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_approved', 'groups', 'user_permissions'), # CRITICAL: Include is_approved
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    # Filters for easy review
    list_filter = ('role', 'is_approved', 'is_active', 'is_staff')
    
    # Add the custom action
    actions = [approve_users]

# Unregister the default UserAdmin and register our custom one
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass
    
admin.site.register(User, CustomUserAdmin)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        'username', 'email', 'first_name', 'last_name', 'student_class', 
        'is_active',  
    )
     
    list_filter = ('student_class', 'is_active')

    search_fields = ('username', 'first_name', 'last_name', 'email')

    # Check your fieldsets definition:
    fieldsets = (
        ('Personal Info', {
            # Make sure 'role' is NOT here.
            'fields': ( 'username', 'first_name', 'last_name', 'email', 
                       'phone_number', 'address', 'password') 
        }),
        ('Academic Info', {
            'fields': ('student_class', 'parents') 
        }),
    )
    
    # You also removed 'role' from get_readonly_fields, which is good:
    def get_readonly_fields(self, request, obj=None):
        if obj:
            # We want to keep this line to prevent editing if the role was initially correct
            return self.readonly_fields + ('role',) 
        return self.readonly_fields
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.role = User.Role.STUDENT 
        
        # Check if this is a NEW user being created (no primary key yet)
        if not instance.pk:
            # Set a placeholder password that cannot be used for login
            instance.set_unusable_password() 
            
        if commit:
            instance.save()
        return instance
    

