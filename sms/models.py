
from django.db import models
from django.db.models import Q
from django.db.models import JSONField
from django.conf import settings
from django.utils import timezone


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
    school_class = models.ForeignKey("SchoolClass", on_delete=models.CASCADE, related_name="exams")
    subject = models.ForeignKey("Subject", on_delete=models.CASCADE, related_name="quizzes")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="exams")
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(default=30)  # length of quiz in minutes
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False)
    allow_retake = models.BooleanField(default=False)  # if true, students can ret
    max_retake_count = models.PositiveIntegerField(default=0)  # 0 = unlimited if allow_retake is True

    def __str__(self):
        return f"{self.title} ({self.subject})"
    
    def total_marks(self):
        return sum(q.marks for q in self.questions.all())


class Question(models.Model):
    QUESTION_TYPES = (
        ("objective", "Objective (single correct)"),
        ("subjective", "Subjective (free text)"),
    )

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    marks = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.text[:50]}  ... ({self.get_question_type_display()})"



class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text} ({'Correct' if self.is_correct else 'Wrong'})"


class StudentExamAttempt(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    exam = models.ForeignKey("Exam", on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)  # quiz expiry
    is_submitted = models.BooleanField(default=False)  # submitted or not
    submitted_at = models.DateTimeField(auto_now_add=True)
    score = models.FloatField(default=0.0)  # score for the attempt
    graded = models.BooleanField(default=False)
    retake_allowed = models.BooleanField(default=False)  # ✅ admin/superadmin override
    retake_count = models.PositiveIntegerField(default=0)  # how many times student retook
    is_retake_approved = models.BooleanField(default=False)
    retake_requested = models.BooleanField(default=False)
    question_order = models.TextField(blank=True, null=True)  # comma-separated question IDs in order


    def can_resume(self):
        """Allow resume if attempt still within time and not submitted."""
        return not self.is_submitted and (self.end_time is None or timezone.now() < self.end_time)

    def can_retake(self):
        """Allow retake if admin has granted it, or quiz allows retakes globally."""
        return self.retake_allowed 

    def __str__(self):
        return f"{self.student} - {self.quiz} (Retakes: {self.retake_count})"



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
        return f"{self.student.username} → {self.quiz.title} ({self.status})"



