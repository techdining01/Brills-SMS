from django.db import models
from accounts.models import User
from django.conf import settings
from django.utils import timezone
from django.db.models import Q


class SchoolClass(models.Model):
    LEVEL_CHOICES = [
        ('kindergarten', 'Kindergarten'),
        ('nursery', 'Nursery'),
        ('primary', 'Primary'),
        ('junior_secondary', 'Junior Secondary'),
        ('senior_secondary', 'Senior Secondary'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    level = models.CharField(
        max_length=20, choices=LEVEL_CHOICES, 
        default='Kindergarten'
    )
    arm = models.CharField(
        max_length=10, blank=True, 
        null=True, help_text="e.g., A, B, C or Science, Arts"
    )
    academic_year = models.DateField(auto_now_add=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    teacher = models.TextField(default='superadmin')
    assistant_teacher = models.TextField(default='superadmin')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Classes"
        ordering = ['name', 'academic_year']
    
    def __str__(self):
        if self.arm:
            return f"{self.name} {self.arm}"
        return self.name


class Subject(models.Model):
    SUBJECT_CATEGORY_CHOICES = [
        ('core', 'Core Subject'),
        ('elective', 'Elective'),
        ('language', 'Language'),
        ('arts', 'Arts'),
        ('sports', 'Sports'),
        ('vocational', 'Vocational'),
    ]
    
   
    code = models.CharField(max_length=20, blank=True)
    name = models.CharField(max_length=100)
    classes = models.ManyToManyField(SchoolClass, related_name='subjects', blank=True)    
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=SUBJECT_CATEGORY_CHOICES, default='core')
    department = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_subjects')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['code', 'name']
    
    def __str__(self):
        return f"{self.code} - {self.name} ({self.get_category_display()})"


class Exam(models.Model):
    title = models.CharField(max_length=200)
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    duration = models.PositiveIntegerField(help_text='Minutes')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False)
    allow_retake = models.BooleanField(default=False) # if true, students can retake


class Question(models.Model):
    EXAM_TYPES = (
    ('objective','Objective'),
    ('subjective','Subjective'),
    )
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    text = models.TextField()
    type = models.CharField(max_length=20, choices=EXAM_TYPES)
    marks = models.PositiveIntegerField(default=1)


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)


class ExamAttempt(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    is_submitted = models.BooleanField(default=False)
    retake_allowed = models.BooleanField(default=False)
    question_order = models.TextField(blank=True, null=True)  # comma-separated question IDs in order


    def can_resume(self):
        """Allow resume if attempt still within time and not submitted."""
        return not self.is_submitted and (self.completed_at is None or timezone.now() < self.end_time)

    def can_retake(self):
        """Allow retake if admin has granted it, or quiz allows retakes globally."""
        return self.retake_allowed 

    def __str__(self):
        return f"{self.student} - {self.exam} "




class StudentAnswer(models.Model):
    attempt = models.ForeignKey(ExamAttempt, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.TextField(blank=True)
    selected_choice = models.ForeignKey(Choice, null=True, blank=True, on_delete=models.SET_NULL)


class SubjectiveMark(models.Model):
    answer = models.OneToOneField(StudentAnswer, on_delete=models.CASCADE)
    score = models.PositiveIntegerField()
    marked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)



class PTARequest(models.Model):
    # Statuses
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        SCHEDULED = 'SCHEDULED', 'Scheduled'
        RESOLVED = 'RESOLVED', 'Resolved'

    # Request types
    class RequestType(models.TextChoices):
        MEETING = 'MEETING', 'Meeting Request'
        ATTENTION = 'ATTENTION', 'Attention Needed'
        MESSAGE = 'MESSAGE', 'General Message'

    parent = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        limit_choices_to=Q(role='PARENT'), 
        related_name='pta_sent'
    )
    # The Staff/Teacher being requested
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        limit_choices_to=Q(role='STAFF'), 
        related_name='pta_received'
    )
    request_type = models.CharField(max_length=10, choices=RequestType.choices)
    title = models.CharField(max_length=100)
    message = models.TextField()
    
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    
    # Optional: For scheduled meetings
    scheduled_time = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.parent.username} - {self.get_request_type_display()} to {self.recipient.username}"
    

class RetakeRequest(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={"role": "student"})
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    reason = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=(("pending", "Pending"), ("approved", "Approved"), ("denied", "Denied")),
        default="pending"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="retake_reviews")

    def __str__(self):
        return f"{self.student.username} → {self.exam.title} ({self.status})"



