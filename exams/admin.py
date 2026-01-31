from django.contrib import admin
from .models import (
    SchoolClass, Subject, Exam, ExamAccess, Question, Choice,
    ExamAttempt, StudentAnswer, SubjectiveMark, RetakeRequest,
    Notification, PTARequest, Broadcast, SystemLog
)


@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'level', 'academic_year', 'teacher', 'is_active']
    list_filter = ['level', 'is_active', 'academic_year']
    search_fields = ['name']


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'department', 'is_active', 'created_by']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'department']


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['title', 'school_class', 'created_by', 'start_time', 'is_published', 'is_active']
    list_filter = ['is_published', 'is_active', 'school_class', 'created_at']
    search_fields = ['title']
    fieldsets = (
        ('Exam Info', {'fields': ('title', 'school_class', 'created_by')}),
        ('Schedule', {'fields': ('start_time', 'end_time', 'duration')}),
        ('Settings', {'fields': ('is_published', 'is_active', 'allow_retake', 'requires_payment', 'price')}),
    )


@admin.register(ExamAccess)
class ExamAccessAdmin(admin.ModelAdmin):
    list_display = ['student', 'exam', 'granted_by', 'via_payment']
    list_filter = ['via_payment', 'granted_at']
    search_fields = ['student__username', 'exam__title']


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 1


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['exam', 'type', 'marks', 'order']
    list_filter = ['type', 'exam']
    search_fields = ['text']
    inlines = [ChoiceInline]


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ['question', 'is_correct']
    list_filter = ['is_correct']


@admin.register(ExamAttempt)
class ExamAttemptAdmin(admin.ModelAdmin):
    list_display = ['student', 'exam', 'status', 'score', 'total_score', 'started_at']
    list_filter = ['status', 'exam', 'started_at']
    search_fields = ['student__username', 'exam__title']
    readonly_fields = ['verification_token', 'started_at', 'last_activity_at']


@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ['attempt', 'question', 'selected_choice']
    list_filter = ['attempt__exam']
    search_fields = ['attempt__student__username']


@admin.register(SubjectiveMark)
class SubjectiveMarkAdmin(admin.ModelAdmin):
    list_display = ['answer', 'score', 'marked_by', 'marked_at']
    list_filter = ['marked_at']
    search_fields = ['answer__attempt__student__username']


@admin.register(RetakeRequest)
class RetakeRequestAdmin(admin.ModelAdmin):
    list_display = ['student', 'exam', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['student__username', 'exam__title']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['sender', 'recipient', 'title', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['title', 'recipient__username']


@admin.register(PTARequest)
class PTARequestAdmin(admin.ModelAdmin):
    list_display = ['parent', 'recipient', 'request_type', 'status', 'created_at']
    list_filter = ['status', 'request_type', 'created_at']
    search_fields = ['parent__username', 'recipient__username']


@admin.register(Broadcast)
class BroadcastAdmin(admin.ModelAdmin):
    list_display = ['sender', 'target_class', 'title', 'created_at']
    list_filter = ['target_class', 'created_at']
    search_fields = ['title', 'message']


@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    list_display = ['level', 'source', 'created_at']
    list_filter = ['level', 'source', 'created_at']
    search_fields = ['message']
    readonly_fields = ['created_at']
