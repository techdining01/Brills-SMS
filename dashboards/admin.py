from django.contrib import admin
from .models import (
    # Phase 5: Question Bank Models
    QuestionBank, QuestionCategory, QuestionTag, QuestionChoice,
    
    # Phase 5: Analytics Models
    ExamAnalytics, StudentPerformance,
    
    # Phase 5: Retakes Models
    AttemptHistory,
    
    # Phase 5: Grading Models
    GradingRubric, RubricCriteria, RubricScore, RubricGrade, RubricCriteriaGrade,
    
    # Phase 5: Scheduling Models
    ExamSchedule, ScheduledNotification,
    
    # Phase 5: Certificate Models
    Certificate, CertificateTemplate,
    
    # Phase 5: Bulk Operations Models
    BulkImportJob, BulkExportJob,
    
    # Phase 5: Permissions Models
    Role, Permission, RolePermission, UserRole,
    
    # Phase 4: Notification Model
    Notification,
)

# ============================================================================
# PHASE 5: QUESTION BANK ADMIN
# ============================================================================

@admin.register(QuestionBank)
class QuestionBankAdmin(admin.ModelAdmin):
    list_display = ('text', 'question_type', 'difficulty', 'category')
    list_filter = ('question_type', 'difficulty', 'category', 'is_published')
    search_fields = ('text', 'explanation')


@admin.register(QuestionCategory)
class QuestionCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'question_count')
    search_fields = ('name',)
    
    def question_count(self, obj):
        return obj.questions.count()
    question_count.short_description = 'Questions'


@admin.register(QuestionTag)
class QuestionTagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(QuestionChoice)
class QuestionChoiceAdmin(admin.ModelAdmin):
    list_display = ('question', 'is_correct')
    list_filter = ('is_correct',)
    search_fields = ('question__text', 'choice_text')
    
    def has_add_permission(self, request):
        return False


# ============================================================================
# PHASE 5: ANALYTICS ADMIN
# ============================================================================

@admin.register(ExamAnalytics)
class ExamAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('exam', 'total_attempts', 'pass_rate', 'average_score')
    list_filter = ('exam',)
    readonly_fields = ('exam',)


@admin.register(StudentPerformance)
class StudentPerformanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'score', 'percentage', 'status')
    list_filter = ('status', 'exam')
    search_fields = ('student__username', 'exam__title')
    readonly_fields = ('student', 'exam')


# ============================================================================
# PHASE 5: ATTEMPT HISTORY ADMIN
# ============================================================================

@admin.register(AttemptHistory)
class AttemptHistoryAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'attempt_number', 'score', 'status')
    list_filter = ('status', 'exam')
    search_fields = ('student__username', 'exam__title')
    readonly_fields = ('student', 'exam')


# ============================================================================
# PHASE 5: GRADING RUBRIC ADMIN
# ============================================================================

# @admin.register(GradingRubric)
class GradingRubricAdmin(admin.ModelAdmin):
    list_display = ('name', 'total_points', 'criteria_count', 'is_published')
    list_filter = ('is_published',)
    search_fields = ('name', 'description')
    
    def criteria_count(self, obj):
        return obj.criteria.count()
    criteria_count.short_description = 'Criteria'


# @admin.register(RubricCriteria)
class RubricCriteriaAdmin(admin.ModelAdmin):
    list_display = ('rubric', 'name', 'max_points', 'order')
    list_filter = ('rubric',)
    search_fields = ('name', 'description')


# @admin.register(RubricScore)
class RubricScoreAdmin(admin.ModelAdmin):
    list_display = ('criteria', 'level', 'points')
    list_filter = ('criteria__rubric',)
    search_fields = ('criteria__name', 'level')
    
    def has_add_permission(self, request):
        return False


# @admin.register(RubricGrade)
class RubricGradeAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'rubric', 'total_score')
    list_filter = ('rubric',)
    readonly_fields = ('attempt', 'rubric')


# @admin.register(RubricCriteriaGrade)
class RubricCriteriaGradeAdmin(admin.ModelAdmin):
    list_display = ('rubric_grade', 'criteria', 'points_awarded', 'comment')
    list_filter = ('criteria__rubric',)
    search_fields = ('rubric_grade__attempt__student__username',)


# ============================================================================
# PHASE 5: SCHEDULING ADMIN
# ============================================================================

@admin.register(ExamSchedule)
class ExamScheduleAdmin(admin.ModelAdmin):
    list_display = ('exam', 'scheduled_date', 'auto_open', 'auto_close', 'status')
    list_filter = ('auto_open', 'auto_close', 'scheduled_date')
    readonly_fields = ('exam', 'created_at')
    
    def status(self, obj):
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        if obj.scheduled_date > now:
            return '📅 Upcoming'
        elif obj.close_at and obj.close_at < now:
            return '✅ Ended'
        return '▶️ Active'
    status.short_description = 'Status'


@admin.register(ScheduledNotification)
class ScheduledNotificationAdmin(admin.ModelAdmin):
    list_display = ('exam', 'student', 'was_successful')
    list_filter = ('was_successful',)
    readonly_fields = ('exam',)
    search_fields = ('exam__title', 'student__username')


# ============================================================================
# PHASE 5: CERTIFICATES ADMIN
# ============================================================================

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('certificate_number', 'student', 'exam', 'grade')
    list_filter = ('grade',)
    search_fields = ('certificate_number', 'student__username', 'exam__title')
    readonly_fields = ('certificate_number', 'verification_code')


@admin.register(CertificateTemplate)
class CertificateTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_default')
    list_filter = ('is_default',)
    search_fields = ('name',)


# ============================================================================
# PHASE 5: BULK OPERATIONS ADMIN
# ============================================================================

@admin.register(BulkImportJob)
class BulkImportJobAdmin(admin.ModelAdmin):
    list_display = ('id', 'import_type', 'status', 'total_rows', 'successful_rows')
    list_filter = ('import_type', 'status')
    readonly_fields = ()
    
    def has_add_permission(self, request):
        return False  # Jobs created via API only


@admin.register(BulkExportJob)
class BulkExportJobAdmin(admin.ModelAdmin):
    list_display = ('id', 'export_type', 'status')
    list_filter = ('export_type', 'status')
    readonly_fields = ()
    
    def has_add_permission(self, request):
        return False  # Jobs created via API only


# ============================================================================
# PHASE 5: PERMISSIONS & ROLES ADMIN
# ============================================================================

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'description')
    search_fields = ('name', 'code')
    list_filter = ('name',)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'role_type', 'permission_count')
    list_filter = ()
    search_fields = ('name',)
    
    def permission_count(self, obj):
        return obj.permissions.count()
    permission_count.short_description = 'Permissions'


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ('role', 'permission')
    list_filter = ('role',)
    search_fields = ('role__name', 'permission__name')


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'is_active')
    list_filter = ('role', 'expires_at')
    search_fields = ('user__username', 'role__name')
    readonly_fields = ()
    
    def is_active(self, obj):
        from datetime import datetime, timezone
        if obj.expires_at:
            return obj.expires_at > datetime.now(timezone.utc)
        return True
    is_active.short_description = 'Active'
    is_active.boolean = True


# ============================================================================
# PHASE 4: NOTIFICATIONS ADMIN
# ============================================================================

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'title', 'is_read')
    list_filter = ('is_read',)
    search_fields = ('recipient__username', 'title', 'message')
    readonly_fields = ('recipient',)
