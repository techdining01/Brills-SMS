from django.contrib import admin
from .models import (
    SchoolClass, Subject, Exam, ExamAccess, Question, Choice, ExamAttempt,
    StudentAnswer, SubjectiveMark, RetakeRequest, PTARequest, Notification,
    Broadcast, SystemLog
)


# =======================
# SchoolClass Admin
# =======================
@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'arm', 'academic_year', 'teacher', 'assistant_teacher', 'is_active')
    list_filter = ('level', 'is_active')
    search_fields = ('name', 'teacher', 'assistant_teacher')
    ordering = ('name', 'academic_year')


# =======================
# Subject Admin
# =======================
@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'category', 'department', 'is_active', 'created_by', 'created_at')
    list_filter = ('category', 'is_active', 'department')
    search_fields = ('code', 'name', 'department', 'created_by__username')
    filter_horizontal = ('classes',)


# =======================
# Exam Admin
# =======================
class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'school_class', 'duration', 'start_time', 'end_time', 'is_active', 'is_published', 'allow_retake', 'requires_payment', 'price', 'created_by', 'created_at')
    list_filter = ('school_class', 'is_active', 'is_published', 'allow_retake', 'requires_payment')
    search_fields = ('title', 'school_class__name', 'created_by__username')
    inlines = [QuestionInline]


# =======================
# ExamAccess Admin
# =======================
@admin.register(ExamAccess)
class ExamAccessAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'granted_by', 'via_payment', 'created_at')
    list_filter = ('via_payment', 'created_at')
    search_fields = ('student__username', 'exam__title', 'granted_by__username')


# =======================
# Question Admin
# =======================
class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'exam', 'type', 'marks')
    list_filter = ('type', 'exam')
    search_fields = ('text', 'exam__title')
    inlines = [ChoiceInline]


# =======================
# ExamAttempt Admin
# =======================
@admin.register(ExamAttempt)
class ExamAttemptAdmin(admin.ModelAdmin):
    list_display = ('exam', 'student', 'status', 'is_submitted', 'retake_allowed', 'started_at', 'completed_at')
    list_filter = ('status', 'is_submitted', 'retake_allowed')
    search_fields = ('exam__title', 'student__username')


# =======================
# StudentAnswer Admin
# =======================
@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'question', 'selected_choice', 'answer_text')
    search_fields = ('attempt__student__username', 'question__text', 'selected_choice__text')


# =======================
# SubjectiveMark Admin
# =======================
@admin.register(SubjectiveMark)
class SubjectiveMarkAdmin(admin.ModelAdmin):
    list_display = ('answer', 'score', 'marked_by')
    search_fields = ('answer__attempt__student__username', 'marked_by__username')


# =======================
# RetakeRequest Admin
# =======================
@admin.register(RetakeRequest)
class RetakeRequestAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'status', 'reviewed_by', 'created_at', 'updated_at')
    list_filter = ('status',)
    search_fields = ('student__username', 'exam__title', 'reviewed_by__username')


# =======================
# PTARequest Admin
# =======================
@admin.register(PTARequest)
class PTARequestAdmin(admin.ModelAdmin):
    list_display = ('parent', 'recipient', 'request_type', 'title', 'status', 'scheduled_time', 'created_at', 'updated_at')
    list_filter = ('request_type', 'status')
    search_fields = ('parent__username', 'recipient__username', 'title')


# =======================
# Notification Admin
# =======================
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'sender', 'recipient', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('title', 'sender__username', 'recipient__username')


# =======================
# Broadcast Admin
# =======================
@admin.register(Broadcast)
class BroadcastAdmin(admin.ModelAdmin):
    list_display = ('title', 'sender', 'target_class', 'created_at')
    search_fields = ('title', 'sender__username', 'target_class__name')


# =======================
# SystemLog Admin
# =======================
@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    list_display = ('level', 'source', 'message', 'created_at')
    list_filter = ('level',)
    search_fields = ('source', 'message')
