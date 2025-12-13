from django.contrib import admin
from django import forms
from django.utils import timezone
from .models import (
    Subject, SchoolClass, Exam, Question, Choice, RetakeRequest,
    StudentExamAttempt, PTARequest, SchoolClass,
)


@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'arm', 'teacher', 'is_active', 'created_at', 'get_total_students')
    list_filter = ('level', 'is_active', 'academic_year')
    search_fields = ('name', 'teacher', 'assistant_teacher')
    
    # NEW METHOD: To display student count
    def get_total_students(self, obj):
        # Assumes User model is correctly linked to SchoolClass via 'students' related_name
        return obj.students.count() 
    get_total_students.short_description = 'Enrolled Students'


# --- 1. Subject Admin (Updated) ---
@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'category', 'is_active', 'get_classes', 'get_total_questions')
    list_filter = ('category', 'is_active', 'department')
    search_fields = ('name', 'code', 'department')
    filter_horizontal = ('classes',) 
    
    # Custom fieldsets for better organization
    fieldsets = (
        (None, {'fields': ('name', 'code', 'category', 'is_active')}),
        ('Curriculum Links', {'fields': ('classes', 'department', 'description')}),
        ('Audit', {'fields': ('created_by', 'created_at')}),
    )
    readonly_fields = ('created_at', 'created_by')
    
    # NEW METHOD: To display linked classes
    def get_classes(self, obj):
        return ", ".join([c.name for c in obj.classes.all()])
    get_classes.short_description = 'Available for'
    
    # NEW METHOD: To display question count (requires CBTQuestion model)
    def get_total_questions(self, obj):
        return obj.cbtquestion_set.count() 
    get_total_questions.short_description = 'Total Qs'



class CsvImportForm(forms.Form):
    csv_file = forms.FileField(help_text="Upload a CSV/Excel file with questions (see template).")



# --- INLINE ADMIN CLASSES ---

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4 # Default 4 choices for Objective questions
    max_num = 6
    fields = ('text', 'is_correct')


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    fields = ('text', 'question_type', 'marks')
    show_change_link = True # Allows staff to click into the Question detail page
    
    # We only show choices for Objective questions
    def get_inlines(self, request, obj=None):
        if obj and obj.question_type == 'objective':
            return [ChoiceInline]
        return []

# --- EXAM ENGINE ADMIN CLASSES ---

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'school_class', 'duration_minutes', 'total_marks', 'is_published', 'created_by')
    list_filter = ('is_published', 'allow_retake', 'subject', 'school_class', 'created_at')
    search_fields = ('title', 'subject__name')
    readonly_fields = ('created_at', 'total_marks')
    
    fieldsets = (
        (None, {'fields': ('title', 'description', 'subject', 'school_class', 'created_by')}),
        ('Scheduling & Rules', {'fields': ('start_time', 'end_time', 'duration_minutes', 'allow_retake', 'max_retake_count')}),
        ('Publication', {'fields': ('is_published',)}),
    )
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('exam', 'text_short', 'question_type', 'marks')
    list_filter = ('exam', 'question_type', 'marks')
    search_fields = ('text', 'exam__title')
    inlines = [ChoiceInline]

    def text_short(self, obj):
        return obj.text[:60] + '...' if len(obj.text) > 60 else obj.text
    text_short.short_description = 'Question Text'


@admin.register(StudentExamAttempt)
class StudentExamAttemptAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'score', 'is_submitted', 'graded', 'can_retake')
    list_filter = ('is_submitted', 'graded', 'exam__subject', 'exam__school_class')
    search_fields = ('student__username', 'exam__title')
    readonly_fields = ('student', 'exam', 'started_at', 'submitted_at', 'end_time', 'question_order')
    actions = ['grade_selected_attempts']

    def grade_selected_attempts(self, request, queryset):
        # MOCK Grading Logic: Calculate score for submitted attempts
        graded_count = 0
        for attempt in queryset.filter(is_submitted=True, graded=False):
            # In a real system, you would iterate over StudentAnswer models here
            # For objective questions: score = sum(1 for correct answers)
            # For subjective questions: staff must manually review and set score
            
            # MOCK IMPLEMENTATION: Just set score to half total marks for demonstration
            total_marks = attempt.exam.total_marks()
            attempt.score = total_marks / 2 
            attempt.graded = True
            attempt.save()
            graded_count += 1
        self.message_user(request, f"Successfully graded {graded_count} submitted attempts.")
    grade_selected_attempts.short_description = "Grade selected submitted attempts (Automatic/Mock)"


@admin.register(RetakeRequest)
class RetakeRequestAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'status', 'created_at', 'reviewed_by')
    list_filter = ('status', 'exam__subject')
    actions = ['approve_retake', 'deny_retake']
    readonly_fields = ('student', 'exam', 'reason', 'created_at')
    
    def approve_retake(self, request, queryset):
        # Approve the request and update the student's latest attempt status
        approved_count = 0
        for req in queryset.filter(status='pending'):
            req.status = 'approved'
            req.reviewed_by = request.user
            req.reviewed_at = timezone.now()
            req.save()
            
            # Find all previous attempts and mark retake_allowed for the next attempt
            StudentExamAttempt.objects.filter(student=req.student, exam=req.exam).update(retake_allowed=True)
            approved_count += 1
        self.message_user(request, f"Approved {approved_count} retake requests.")
    approve_retake.short_description = "Approve selected retake requests"
    
    def deny_retake(self, request, queryset):
        queryset.filter(status='pending').update(status='denied', reviewed_by=request.user, reviewed_at=timezone.now())
        self.message_user(request, f"Denied {queryset.count()} retake requests.")
    deny_retake.short_description = "Deny selected retake requests"



# --- 4. PTA Request Admin (No fix needed) ---
@admin.register(PTARequest)
class PTARequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'parent', 'recipient', 'request_type', 'status', 'scheduled_time')
    list_filter = ('status', 'request_type')
    search_fields = ('title', 'parent__username', 'recipient__username')
    readonly_fields = ('parent', 'created_at')
    
    fieldsets = (
        (None, {'fields': ('parent', 'recipient', 'title', 'request_type', 'message')}),
        ('Resolution', {'fields': ('status', 'scheduled_time')}),
    )
