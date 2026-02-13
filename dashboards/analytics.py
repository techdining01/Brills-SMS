"""
Analytics module for exam statistics and performance tracking
"""
from django.db.models import Avg, Count, Q, F, Max, Min
from django.utils import timezone
from datetime import timedelta
from exams.models import ExamAttempt
from .models import ExamAnalytics, StudentPerformance, AttemptHistory


def update_exam_analytics(exam):
    """Update analytics for an exam"""
    attempts = ExamAttempt.objects.filter(
        exam=exam,
        status='submitted'
    )
    
    if not attempts.exists():
        return None
    
    total_attempts = attempts.count()
    
    scores = [att.total_score for att in attempts]
    passed_count = sum(1 for score in scores if score >= exam.passing_marks)
    
    average_score = sum(scores) / len(scores) if scores else 0
    highest_score = max(scores) if scores else 0
    lowest_score = min(scores) if scores else 0
    
    time_taken_list = [
        max(0, (att.completed_at - att.started_at).total_seconds())
        for att in attempts
        if att.completed_at and att.started_at
    ]
    average_time = sum(time_taken_list) / len(time_taken_list) if time_taken_list else 0
    
    pass_rate = (passed_count / total_attempts * 100) if total_attempts > 0 else 0
    
    analytics, _ = ExamAnalytics.objects.update_or_create(
        exam=exam,
        defaults={
            'total_attempts': total_attempts,
            'total_passed': passed_count,
            'average_score': average_score,
            'highest_score': highest_score,
            'lowest_score': lowest_score,
            'average_time_taken': max(0, int(average_time)),
            'pass_rate': pass_rate,
        }
    )
    
    return analytics


def get_exam_statistics(exam):
    """Get detailed statistics for an exam"""
    analytics = ExamAnalytics.objects.filter(exam=exam).first()
    
    attempts = ExamAttempt.objects.filter(
        exam=exam,
        status='submitted'
    )
    
    # Question difficulty analysis
    question_stats = []
    for question in exam.questions.all():
        correct_count = attempts.filter(
            answers__question=question,
            answers__selected_choice__is_correct=True
        ).distinct().count()
        
        question_stats.append({
            'question': question,
            'correct': correct_count,
            'total_attempts': attempts.count(),
            'accuracy': (correct_count / attempts.count() * 100) if attempts.count() > 0 else 0,
        })
    
    return {
        'analytics': analytics,
        'question_stats': question_stats,
        'attempts': attempts.count(),
    }


def get_student_performance_summary(student, limit=10):
    """Get performance summary for a student"""
    performances = StudentPerformance.objects.filter(
        student=student
    ).order_by('-attempted_at')[:limit]
    
    total_attempts = StudentPerformance.objects.filter(student=student).count()
    passed = StudentPerformance.objects.filter(student=student, status='passed').count()
    
    avg_percentage = StudentPerformance.objects.filter(
        student=student
    ).aggregate(avg=Avg('percentage'))['avg'] or 0
    
    return {
        'performances': performances,
        'total_attempts': total_attempts,
        'passed': passed,
        'failed': total_attempts - passed,
        'pass_rate': (passed / total_attempts * 100) if total_attempts > 0 else 0,
        'average_percentage': avg_percentage,
    }


def get_class_analytics(school_class):
    """Get analytics for an entire class"""
    exams = school_class.exam_set.all()
    
    analytics_data = {
        'total_exams': exams.count(),
        'total_students': school_class.students.count(),
        'exams': [],
    }
    
    for exam in exams:
        analytics = ExamAnalytics.objects.filter(exam=exam).first()
        if analytics:
            analytics_data['exams'].append({
                'exam': exam,
                'analytics': analytics,
            })
    
    return analytics_data


def get_performance_trend(student, exam=None, days=30):
    """Get performance trend for a student over time"""
    since = timezone.now() - timedelta(days=days)
    
    query = StudentPerformance.objects.filter(
        student=student,
        attempted_at__gte=since
    )
    
    if exam:
        query = query.filter(exam=exam)
    
    return query.order_by('attempted_at')


def calculate_performance_metrics(attempt):
    """Calculate and store performance metrics for an attempt"""
    if attempt.status != 'submitted':
        return None
    
    if attempt.completed_at and attempt.started_at:
        time_taken = max(0, (attempt.completed_at - attempt.started_at).total_seconds())
    else:
        time_taken = 0

    total_marks = sum([q.marks for q in attempt.exam.questions.all()])
    percentage = (attempt.total_score / total_marks * 100) if total_marks > 0 else 0
    
    # Determine pass/fail (assuming 60% is passing grade)
    passing_percentage = 60
    status = 'passed' if percentage >= passing_percentage else 'failed'
    
    performance, _ = StudentPerformance.objects.get_or_create(
        student=attempt.student,
        exam=attempt.exam,
        attempt_number=1,  # Can be updated to track multiple attempts
        defaults={
            'score': attempt.total_score,
            'total_marks': total_marks,
            'percentage': percentage,
            'time_taken': int(time_taken),
            'status': status,
        }
    )
    
    # Update attempt history
    AttemptHistory.objects.get_or_create(
        student=attempt.student,
        exam=attempt.exam,
        attempt_number=1,
        defaults={
            'score': attempt.total_score,
            'total_marks': total_marks,
            'percentage': percentage,
            'status': status,
            'time_taken': int(time_taken),
            'submitted_at': attempt.completed_at,
            'attempt': attempt,
        }
    )
    
    return performance


def get_top_performers(exam, limit=10):
    """Get top performing students for an exam"""
    return StudentPerformance.objects.filter(
        exam=exam
    ).order_by('-percentage')[:limit]


def get_bottom_performers(exam, limit=10):
    """Get bottom performing students for an exam"""
    return StudentPerformance.objects.filter(
        exam=exam
    ).order_by('percentage')[:limit]


def get_most_difficult_questions(exam):
    """Get questions where students performed worst"""
    attempts = ExamAttempt.objects.filter(
        exam=exam,
        status='submitted'
    ).count()
    
    if attempts == 0:
        return []
    
    question_difficulty = []
    for question in exam.questions.all():
        correct_count = ExamAttempt.objects.filter(
            exam=exam,
            status='submitted',
            answers__question=question,
            answers__selected_choice__is_correct=True
        ).count()
        
        accuracy = (correct_count / attempts * 100)
        question_difficulty.append({
            'question': question,
            'accuracy': accuracy,
            'correct': correct_count,
            'total': attempts,
        })
    
    # Sort by accuracy (ascending)
    return sorted(question_difficulty, key=lambda x: x['accuracy'])


def get_performance_by_question_type(exam):
    """Get performance metrics by question type"""
    attempts = ExamAttempt.objects.filter(
        exam=exam,
        status='submitted'
    )
    
    results = {}
    for q_type in ['objective', 'subjective']:
        questions = exam.questions.filter(type=q_type)
        total_marks = sum([q.marks for q in questions])
        
        if total_marks > 0:
            avg_score = attempts.aggregate(
                avg=Avg(F('score'))
            )['avg'] or 0
            
            results[q_type] = {
                'total_marks': total_marks,
                'average_score': avg_score,
                'questions': questions.count(),
            }
    
    return results
