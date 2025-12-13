from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Q
from PIL import Image
from django.utils import timezone 
from sms.models import SchoolClass
from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model
from django.contrib.auth.models import BaseUserManager


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        STAFF = "STAFF", "Staff"
        PARENT = "PARENT", "Parent"
        STUDENT = "STUDENT", "Student"

    base_role = Role.STUDENT

    role = models.CharField(
        max_length=50,
        choices=Role.choices,
        default=Role.STUDENT,
        help_text="Role of the user in the school management system."
        )

    student_class = models.ForeignKey(
        SchoolClass, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='students',
        help_text="The academic class this student belongs to."
    )

    parents = models.ManyToManyField(
        'self', # Self-referential Many-to-Many relationship
        limit_choices_to=Q(role='PARENT'), # Only allow users with role='PARENT'
        symmetrical=False,
        blank=True,
        related_name='children', # Access: parent_user.children.all()
        verbose_name='Parent/Guardian'
    )

    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    emergency_contact = models.CharField(max_length=100, blank=True)
    emergency_phone = models.CharField(max_length=15, blank=True)
    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)

    profile_picture = models.ImageField(
        upload_to='user_profiles/',     # Saves files to /media/user_profiles/ in S3
        null=True, 
        blank=True,
        help_text="User profile image"
    )

     # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def save(self, *args, **kwargs):
        if not self.pk:
            self.role = self.base_role

        if not self.username:
            # Ensure email is lowercase
            self.email = self.email.lower()

        #Resize profile picture
        if self.profile_picture and hasattr(self.profile_picture, 'path'):
            try:
                img = Image.open(self.profile_picture.path)
                if img.height > 300 or img.width > 300:
                    output_size = (300, 300)
                    img.thumbnail(output_size)
                    img.save(self.profile_picture.path, optimize=True, quality=85)
            except (FileNotFoundError, ValueError):
                pass
    

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_role_display()} - {self.username}"
    

# ==============================================================================

class CustomRoleManager(BaseUserManager):
    """
    A base class for role managers, inheriting BaseUserManager 
    for compatibility with Django's authentication system and email normalization.
    """
    
    # Required method inherited from BaseUserManager
    def normalize_email(self, email):
        return BaseUserManager.normalize_email(email)

    # Required method inherited from BaseUserManager
    def get_queryset(self):
        # This will be overridden in the specific role managers below
        return super().get_queryset()
        
    # These methods are often required if you create users directly via the manager
    def create_user(self, username, email, password=None, **extra_fields):
        # A minimal implementation
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        # The role filter is applied by the subclass's manager
        user.save(using=self._db)
        return user


# ==============================================================================
# 2. Role-Specific Managers
# ==============================================================================

class StudentManager(CustomRoleManager):
    """Custom manager for the Student proxy model."""
    def get_queryset(self):
        return super().get_queryset().filter(role=User.Role.STUDENT)

class ParentManager(CustomRoleManager):
    """Custom manager for the Parent proxy model."""
    def get_queryset(self):
        # CRITICAL: Filters the User queryset to only include PARENT roles
        return super().get_queryset().filter(role=User.Role.PARENT)

class StaffManager(CustomRoleManager):
    """Custom manager for the Staff proxy model."""
    def get_queryset(self):
        # CRITICAL: Filters the User queryset to only include STAFF roles
        return super().get_queryset().filter(role=User.Role.STAFF)


# ==============================================================================
# 3. Proxy Models
# ==============================================================================

class Student(User):
    base_role = User.Role.STUDENT

    admission_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Admission Number',
        blank=True, 
        null=True
    )
  
    objects = StudentManager()

    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
     
    @staticmethod
    def generate_unique_reg_no():
        """
        Generates a unique registration number in format:
        TBS/2025/AB93K  (crypto-safe, collision-free)
        """
        year = timezone.now().year
        random_part = get_random_string(length=5).upper()
        return f"TBS/{year}/{random_part}"
    
    @classmethod
    def create_unique_reg_no(cls):
        """Ensures the generated number is always unique."""
        reg_no = cls.generate_unique_reg_no()
        # FIX: Check against 'admission_number', not 'registration_number'
        while cls.objects.filter(admission_number=reg_no).exists(): 
            reg_no = cls.generate_unique_reg_no()
        return reg_no

    def save(self, *args, **kwargs):
        # Generate unique admission number for students only
        # FIX: Check against 'admission_number', and use cls/self for the method call
        if self.role == self.base_role and not self.admission_number: 
            self.admission_number = self.create_unique_reg_no()
        
        # Call the parent User's save method to handle profile picture resizing and base logic
        super().save(*args, **kwargs)


class Parent(User):
    """
    Proxy model for Parent/Guardian users.
    Filters the base User model to only include users with the PARENT role.
    """
    base_role = User.Role.PARENT
    
    # CRITICAL: Assign the custom manager to ensure proper filtering.
    # Assumes ParentManager class is defined above/imported correctly.
    objects = ParentManager() 

    class Meta:
        proxy = True  # Defines this as a proxy model (no new table created)
        verbose_name = "Parent/Guardian"
        verbose_name_plural = "Parents/Guardians"

    def get_full_name(self):
        # A utility method specific to this role, if needed.
        return f"{self.first_name} {self.last_name}"


class Staff(User):
    """
    Proxy model for Staff users (Teachers, Non-Teaching Staff).
    Filters the base User model to only include users with the STAFF role.
    """
    base_role = User.Role.STAFF
    
    # CRITICAL: Assign the custom manager to ensure proper filtering.
    # Assumes StaffManager class is defined above/imported correctly.
    objects = StaffManager()

    class Meta:
        proxy = True
        verbose_name = "Staff Member"
        verbose_name_plural = "Staff Members"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    @staticmethod
    def generate_unique_reg_no():
        """
        Generates a unique registration number in format:
        TBS/STF/2025/AB93K  (crypto-safe, collision-free)
        """
        year = timezone.now().year
        random_part = get_random_string(length=5).upper()
        return f"TBS/STF/{year}/{random_part}"
    
    @classmethod
    def create_unique_reg_no(cls):
        """Ensures the generated number is always unique."""
        reg_no = cls.generate_unique_reg_no()
        # FIX: Check against 'admission_number', not 'registration_number'
        while cls.objects.filter(admission_number=reg_no).exists(): 
            reg_no = cls.generate_unique_reg_no()
        return reg_no

    def save(self, *args, **kwargs):
        # Generate unique admission number for students only
        # FIX: Check against 'admission_number', and use cls/self for the method call
        if self.role == self.base_role and not self.admission_number: 
            self.admission_number = self.create_unique_reg_no()
        
        # Call the parent User's save method to handle profile picture resizing and base logic
        super().save(*args, **kwargs)