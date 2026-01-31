"""
Exam scheduling and auto-open/close functionality
"""
from django.utils import timezone
from django.db import transaction
from exams.models import Exam, ExamAttempt
from .models import ExamSchedule, ScheduledNotification
from .notification_handlers import send_notification



def schedule_exam(exam, scheduled_date, auto_open=True, auto_close=True, 
                 close_at=None, notify_before_minutes=15):
    """Create or update exam schedule"""
    schedule, created = ExamSchedule.objects.update_or_create(
        exam=exam,
        defaults={
            'scheduled_date': scheduled_date,
            'auto_open': auto_open,
            'auto_close': auto_close,
            'close_at': close_at,
            'notify_before_minutes': notify_before_minutes,
        }
    )
    return schedule


def get_upcoming_exams(days=7):
    """Get exams scheduled in the next N days"""
    now = timezone.now()
    upcoming_date = now + timezone.timedelta(days=days)
    
    return ExamSchedule.objects.filter(
        scheduled_date__gte=now,
        scheduled_date__lte=upcoming_date,
        auto_open=True
    ).select_related('exam')


def get_exam_schedule(exam):
    """Get schedule for specific exam"""
    return ExamSchedule.objects.filter(exam=exam).first()


def process_scheduled_exams():
    """
    Process scheduled exams - open/close as needed
    Should be run via management command or Celery task
    """
    now = timezone.now()
    
    # Get all scheduled exams
    schedules = ExamSchedule.objects.filter(auto_open=True)
    
    opened_count = 0
    closed_count = 0
    
    for schedule in schedules:
        exam = schedule.exam
        
        # Check if exam should be opened
        if (schedule.scheduled_date <= now and 
            exam.is_active and 
            not exam.is_published):
            
            exam.is_published = True
            exam.save(update_fields=['is_published'])
            opened_count += 1
            
            # Send notifications to students
            notify_students_exam_opened(exam)
        
        # Check if exam should be closed
        if (schedule.auto_close and 
            schedule.close_at and 
            schedule.close_at <= now):
            
            exam.is_active = False
            exam.save(update_fields=['is_active'])
            closed_count += 1
            
            # Auto-submit all in-progress attempts
            if schedule.auto_submit_at_time:
                auto_submit_attempts(exam)
    
    return {
        'opened': opened_count,
        'closed': closed_count,
    }


def notify_students_before_exam(exam):
    """
    Notify students about upcoming exam
    Should be run via management command or Celery task
    """
    schedule = ExamSchedule.objects.filter(exam=exam).first()
    
    if not schedule:
        return 0
    
    now = timezone.now()
    notify_time = schedule.scheduled_date - timezone.timedelta(
        minutes=schedule.notify_before_minutes
    )
    
    # Check if it's time to notify
    if now < notify_time or now > schedule.scheduled_date:
        return 0
    
    # Get students in the class
    students = exam.school_class.students.filter(is_active=True)
    
    notified_count = 0
    for student in students:
        # Check if already notified
        already_notified = ScheduledNotification.objects.filter(
            exam=exam,
            student=student
        ).exists()
        
        if not already_notified:
            try:
                send_notification(
                    recipient=student,
                    title=f"Upcoming Exam: {exam.title}",
                    message=f"Your exam '{exam.title}' will start in {schedule.notify_before_minutes} minutes.",
                    category='warning',
                    related_exam=exam,
                )
                
                ScheduledNotification.objects.create(
                    exam=exam,
                    student=student,
                    was_successful=True,
                )
                notified_count += 1
            
            except Exception as e:
                ScheduledNotification.objects.create(
                    exam=exam,
                    student=student,
                    was_successful=False,
                )
    
    return notified_count


def notify_students_exam_opened(exam):
    """Notify students that exam is now open"""
    students = exam.school_class.students.filter(is_active=True)
    
    for student in students:
        send_notification(
            recipient=student,
            title=f"Exam Started: {exam.title}",
            message=f"The exam '{exam.title}' is now open. Click to start.",
            category='info',
            related_exam=exam,
        )


def auto_submit_attempts(exam):
    """Auto-submit all in-progress exam attempts"""
    in_progress = ExamAttempt.objects.filter(
        exam=exam,
        status__in=['in_progress', 'interrupted']
    )
    
    submitted_count = 0
    
    for attempt in in_progress:
        attempt.status = 'submitted'
        attempt.completed_at = timezone.now()
        attempt.save(update_fields=['status', 'completed_at'])
        submitted_count += 1
        
        # Notify student
        send_notification(
            recipient=attempt.student,
            title="Exam Auto-Submitted",
            message=f"Your exam '{exam.title}' has been auto-submitted as time expired.",
            category='info',
            related_exam=exam,
        )
    
    return submitted_count


def get_schedule_info(exam):
    """Get human-readable schedule information"""
    schedule = ExamSchedule.objects.filter(exam=exam).first()
    
    if not schedule:
        return None
    
    now = timezone.now()
    scheduled_date = schedule.scheduled_date
    
    # Calculate time until exam
    time_diff = scheduled_date - now
    
    if time_diff.total_seconds() < 0:
        status = "Started"
        time_text = ""
    elif time_diff.days > 0:
        status = "Upcoming"
        time_text = f"{time_diff.days} days, {time_diff.seconds // 3600} hours"
    elif time_diff.seconds > 3600:
        status = "Starting Soon"
        hours = time_diff.seconds // 3600
        minutes = (time_diff.seconds % 3600) // 60
        time_text = f"{hours}h {minutes}m"
    else:
        status = "Starting Very Soon"
        minutes = time_diff.seconds // 60
        time_text = f"{minutes} minutes"
    
    return {
        'schedule': schedule,
        'status': status,
        'time_until': time_text,
        'scheduled_date': scheduled_date,
        'is_past': time_diff.total_seconds() < 0,
    }


def reschedule_exam(exam, new_date):
    """Reschedule an exam to a new date"""
    schedule = ExamSchedule.objects.filter(exam=exam).first()
    
    if schedule:
        schedule.scheduled_date = new_date
        schedule.save(update_fields=['scheduled_date'])
        
        # Notify students about reschedule
        students = exam.school_class.students.filter(is_active=True)
        for student in students:
            send_notification(
                recipient=student,
                title=f"Exam Rescheduled: {exam.title}",
                message=f"The exam '{exam.title}' has been rescheduled to {new_date.strftime('%Y-%m-%d %H:%M')}.",
                category='warning',
                related_exam=exam,
            )
        
        return True
    
    return False


def cancel_exam_schedule(exam):
    """Cancel exam schedule"""
    schedule = ExamSchedule.objects.filter(exam=exam).first()
    
    if schedule:
        exam.is_active = False
        exam.save(update_fields=['is_active'])
        
        schedule.delete()
        
        # Notify students
        students = exam.school_class.students.filter(is_active=True)
        for student in students:
            send_notification(
                recipient=student,
                title=f"Exam Cancelled: {exam.title}",
                message=f"The exam '{exam.title}' has been cancelled.",
                category='error',
                related_exam=exam,
            )
        
        return True
    
    return False
