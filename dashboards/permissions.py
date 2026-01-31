"""
Advanced permissions and role-based access control
"""
from .models import Role, Permission, RolePermission, UserRole
from functools import wraps
from django.http import HttpResponseForbidden
from django.utils import timezone


def initialize_default_permissions():
    """Create default permissions if they don't exist"""
    permission_data = [
        # Exam Management
        ('create_exam', 'Create Exam', 'Create new exams', 'exam_management'),
        ('edit_exam', 'Edit Exam', 'Edit existing exams', 'exam_management'),
        ('delete_exam', 'Delete Exam', 'Delete exams', 'exam_management'),
        ('publish_exam', 'Publish Exam', 'Publish exams for students', 'exam_management'),
        ('schedule_exam', 'Schedule Exam', 'Schedule exams for future dates', 'exam_management'),
        ('manage_exam_access', 'Manage Exam Access', 'Grant individual exam access', 'exam_management'),
        
        # Grading
        ('grade_exam', 'Grade Exam', 'Grade subjective answers', 'grading'),
        ('create_rubric', 'Create Rubric', 'Create grading rubrics', 'grading'),
        ('edit_rubric', 'Edit Rubric', 'Edit grading rubrics', 'grading'),
        ('view_grades', 'View Grades', 'View all exam grades', 'grading'),
        
        # Analytics
        ('view_analytics', 'View Analytics', 'View exam statistics', 'analytics'),
        ('view_class_analytics', 'View Class Analytics', 'View class performance', 'analytics'),
        ('view_student_analytics', 'View Student Analytics', 'View individual student performance', 'analytics'),
        ('export_analytics', 'Export Analytics', 'Export analytics data', 'analytics'),
        
        # Student Management
        ('manage_students', 'Manage Students', 'Add/edit/delete students', 'student_management'),
        ('bulk_import_students', 'Bulk Import Students', 'Import students from CSV', 'student_management'),
        ('view_student_list', 'View Student List', 'View all students', 'student_management'),
        
        # Question Bank
        ('create_question', 'Create Question', 'Create questions in bank', 'question_bank'),
        ('edit_question', 'Edit Question', 'Edit bank questions', 'question_bank'),
        ('delete_question', 'Delete Question', 'Delete bank questions', 'question_bank'),
        ('bulk_import_questions', 'Bulk Import Questions', 'Import questions from CSV', 'question_bank'),
        ('publish_question', 'Publish Question', 'Publish questions for use', 'question_bank'),
        
        # Certificate
        ('issue_certificate', 'Issue Certificate', 'Issue certificates to students', 'certificate'),
        ('revoke_certificate', 'Revoke Certificate', 'Revoke issued certificates', 'certificate'),
        ('view_certificate', 'View Certificate', 'View student certificates', 'certificate'),
        ('create_certificate_template', 'Create Template', 'Create certificate templates', 'certificate'),
        
        # Bulk Operations
        ('bulk_import', 'Bulk Import', 'Import data in bulk', 'bulk_operations'),
        ('bulk_export', 'Bulk Export', 'Export data in bulk', 'bulk_operations'),
        ('manage_import_jobs', 'Manage Import Jobs', 'Manage bulk import jobs', 'bulk_operations'),
    ]
    
    for code, name, description, category in permission_data:
        Permission.objects.get_or_create(
            code=code,
            defaults={
                'name': name,
                'description': description,
                'category': category,
            }
        )


def initialize_default_roles():
    """Create default roles with permissions"""
    initialize_default_permissions()
    
    # Teacher role
    teacher_role, _ = Role.objects.get_or_create(
        name='Teacher',
        defaults={
            'role_type': 'teacher',
            'description': 'Teacher with exam and grading rights',
            'is_active': True,
        }
    )
    
    teacher_permissions = [
        'create_exam', 'edit_exam', 'publish_exam',
        'grade_exam', 'create_rubric', 'edit_rubric',
        'view_analytics', 'view_student_analytics',
        'create_question', 'edit_question',
        'manage_exam_access',
    ]
    
    for perm_code in teacher_permissions:
        perm = Permission.objects.get(code=perm_code)
        RolePermission.objects.get_or_create(
            role=teacher_role,
            permission=perm,
        )
    
    # Department Head role
    dept_head_role, _ = Role.objects.get_or_create(
        name='Department Head',
        defaults={
            'role_type': 'department_head',
            'description': 'Department head with extended permissions',
            'is_active': True,
        }
    )
    
    dept_head_permissions = teacher_permissions + [
        'view_class_analytics', 'delete_exam',
        'manage_students', 'bulk_import_students',
        'bulk_import_questions', 'issue_certificate',
    ]
    
    for perm_code in dept_head_permissions:
        perm = Permission.objects.get(code=perm_code)
        RolePermission.objects.get_or_create(
            role=dept_head_role,
            permission=perm,
        )
    
    # Exam Coordinator role
    coordinator_role, _ = Role.objects.get_or_create(
        name='Exam Coordinator',
        defaults={
            'role_type': 'exam_coordinator',
            'description': 'Coordinates exams and manage schedules',
            'is_active': True,
        }
    )
    
    coordinator_permissions = [
        'create_exam', 'edit_exam', 'publish_exam',
        'schedule_exam', 'manage_exam_access',
        'view_analytics', 'view_class_analytics',
        'bulk_import', 'bulk_export',
        'manage_import_jobs',
    ]
    
    for perm_code in coordinator_permissions:
        perm = Permission.objects.get(code=perm_code)
        RolePermission.objects.get_or_create(
            role=coordinator_role,
            permission=perm,
        )


def user_has_permission(user, permission_code):
    """Check if user has specific permission"""
    if user.is_superuser or user.is_staff:
        return True
    
    user_roles = UserRole.objects.filter(user=user)
    
    for user_role in user_roles:
        if user_role.expires_at and user_role.expires_at < timezone.now():
            continue
        
        has_perm = RolePermission.objects.filter(
            role=user_role.role,
            permission__code=permission_code
        ).exists()
        
        if has_perm:
            return True
    
    return False


def require_permission(permission_code):
    """Decorator to require permission for view"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not user_has_permission(request.user, permission_code):
                return HttpResponseForbidden("You don't have permission to access this resource.")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def get_user_permissions(user):
    """Get all permissions for a user"""
    if user.is_superuser:
        return Permission.objects.all()
    
    user_roles = UserRole.objects.filter(user=user)
    permissions = set()
    
    for user_role in user_roles:
        if user_role.expires_at and user_role.expires_at < timezone.now():
            continue
        
        role_perms = RolePermission.objects.filter(
            role=user_role.role
        ).values_list('permission', flat=True)
        
        permissions.update(role_perms)
    
    return Permission.objects.filter(id__in=permissions)


def get_user_roles(user):
    """Get all active roles for a user"""
    user_roles = UserRole.objects.filter(user=user)
    active_roles = []
    
    for user_role in user_roles:
        if not user_role.expires_at or user_role.expires_at > timezone.now():
            active_roles.append(user_role.role)
    
    return active_roles


def assign_role_to_user(user, role, assigned_by, expires_at=None):
    """Assign role to user"""
    user_role, created = UserRole.objects.update_or_create(
        user=user,
        role=role,
        defaults={
            'assigned_by': assigned_by,
            'expires_at': expires_at,
        }
    )
    return user_role


def remove_role_from_user(user, role):
    """Remove role from user"""
    UserRole.objects.filter(user=user, role=role).delete()


def revoke_expired_roles():
    """Revoke all expired roles (run periodically)"""
    from django.utils import timezone
    UserRole.objects.filter(
        expires_at__lt=timezone.now()
    ).delete()
