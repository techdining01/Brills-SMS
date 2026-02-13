"""
PHASE 2: EXAM TAKING INTERFACE
- Exam taking with timer
- Auto-save functionality
- Question navigation
- Answer recording
- Submit & auto-grade objective questions
"""


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.db.models import Count
from django.utils import timezone
from django.db import transaction
from django.contrib import messages
import json

from accounts.models import User
from exams.models import (
    Exam, ExamAttempt, Question, Choice, StudentAnswer,
    SubjectiveMark, ExamAccess, Notification, SystemLog
)


# ========================= EXAM TAKING VIEWS =========================

@login_required()
@require_http_methods(["GET"])
def start_exam(request, exam_id):
    """
    Start an exam - create attempt or resume if exists
    GET: Display exam details and instructions
    """
    exam = get_object_or_404(Exam, id=exam_id)
    student = request.user
    
    # Check if student can take this exam
    if not _can_take_exam(student, exam):
        return JsonResponse({
            'error': 'You do not have access to this exam'
        }, status=403)
    
    # Check for active attempt
    active_attempt = ExamAttempt.objects.filter(
        student=student,
        exam=exam,
        status__in=['in_progress', 'interrupted']
    ).first()
    
    if active_attempt:
        # Resume existing attempt
        return redirect('dashboards:take_exam', attempt_id=active_attempt.id)
    
    # Check if exam has started
    if exam.start_time > timezone.now():
        return render(request, 'exams/exam_not_started.html', {
            'exam': exam,
            'time_until_start': exam.start_time - timezone.now()
        })
    
    # Check if exam has ended
    if exam.end_time < timezone.now():
        return render(request, 'exams/exam_ended.html', {
            'exam': exam,
            'message': 'This exam has ended'
        })
    
    # Show exam instructions
    return render(request, 'exams/exam_instructions.html', {
        'exam': exam,
        'questions_count': exam.questions.count(),
        'total_marks': exam.questions.aggregate(
            total=Count('id')
        )['total'] or 0,
        'duration_minutes': exam.duration
    })


@login_required()
@require_http_methods(["POST"])
def create_exam_attempt(request, exam_id):
    """
    Create a new exam attempt and redirect to taking
    POST: Create attempt and start exam
    """
    exam = get_object_or_404(Exam, id=exam_id)
    student = request.user
    
    # Verify access
    if not _can_take_exam(student, exam):
        messages.error(request, 'You do not have access to this exam')
        return redirect('dashboards:student_available_exams')
    
    # Check existing active attempt
    active_attempt = ExamAttempt.objects.filter(
        student=student,
        exam=exam,
        status__in=['in_progress', 'interrupted']
    ).first()
    
    if active_attempt:
        return redirect('dashboards:take_exam', attempt_id=active_attempt.id)
    
    # Create new attempt
    with transaction.atomic():
        attempt = ExamAttempt.objects.create(
            student=student,
            exam=exam,
            status='in_progress',
            started_at=timezone.now(),
            remaining_seconds=exam.duration * 60
        )
        
        # Log system event
        SystemLog.objects.create(
            level='INFO',
            message=f'Student {student.username} started exam: {exam.title}',
            created_at=timezone.now()
        )
        
        # Create notification
        if exam.created_by != student:
            Notification.objects.create(
                sender=student,
                recipient=exam.created_by,
                title='exam_started',
                message=f'{student.get_full_name()} started exam: {exam.title}',
                related_exam=exam.id
            )
    
    return redirect('dashboards:take_exam', attempt_id=attempt.id)


@login_required()
@require_http_methods(["GET"])
def take_exam(request, attempt_id):
    """
    Main exam taking interface with timer and question navigation
    GET: Display exam taking page with all questions
    """
    attempt = get_object_or_404(
        ExamAttempt.objects.select_related('exam', 'student'),
        id=attempt_id
    )
    
    # Verify ownership
    if attempt.student != request.user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    # Check if exam has ended
    if attempt.status == 'submitted':
        return JsonResponse({'error': 'Exam already submitted'}, status=400)
    
    if attempt.exam.end_time < timezone.now():
        return redirect('dashboards:submit_exam', attempt_id=attempt.id)
    
    # Calculate time remaining
    elapsed = (timezone.now() - attempt.started_at).total_seconds()
    total_seconds = attempt.exam.duration * 60
    time_remaining = max(0, total_seconds - elapsed)
    
    # Auto-submit if time's up
    if time_remaining <= 0:
        return redirect('dashboards:submit_exam', attempt_id=attempt.id)
    
    # Get all questions
    questions = attempt.exam.questions.prefetch_related(
        'choices'
    ).order_by('order')
    
    # Get student's current answers
    student_answers = StudentAnswer.objects.filter(
        attempt=attempt
    ).select_related('selected_choice')
    
    # Build answer map
    answers_map = {
        answer.question_id: {
            'selected_choice_id': answer.selected_choice_id,
            'answer_text': answer.answer_text
        }
        for answer in student_answers
    }
    
    # Current question (from GET param or first unanswered)
    current_question_id = request.GET.get('question_id')
    if current_question_id:
        current_question = questions.filter(id=current_question_id).first()
    else:
        current_question = questions.first()
    
    # Get current answer if exists
    current_answer = None
    if current_question and current_question.id in answers_map:
        current_answer = answers_map[current_question.id]

    # Question navigation data
    questions_data = []
    for i, q in enumerate(questions, 1):
        is_answered = q.id in answers_map
        questions_data.append({
            'id': q.id,
            'number': i,
            'type': q.type,
            'is_answered': is_answered,
            'is_current': q.id == current_question.id if current_question else False
        })
    
    return render(request, 'exams/take_exam.html', {
        'attempt': attempt,
        'exam': attempt.exam,
        'current_question': current_question,
        'current_answer': current_answer,
        'questions': questions,
        'questions_data': questions_data,
        'answers_map': answers_map,
        'total_questions': questions.count(),
        'answered_questions': len(answers_map),
        'time_remaining_seconds': int(time_remaining),
        'time_remaining_display': f"{int(time_remaining // 60)}:{int(time_remaining % 60):02d}",
        'duration_minutes': attempt.exam.duration
    })


@login_required()
@require_http_methods(["POST"])
def save_answer(request, attempt_id):
    """
    Save a single answer (AJAX auto-save)
    POST: Save answer and return status
    """
    try:
        attempt = ExamAttempt.objects.get(id=attempt_id)
    except ExamAttempt.DoesNotExist:
        return JsonResponse({'error': 'Exam attempt not found'}, status=404)
    
    # Verify ownership
    if attempt.student != request.user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    # Check exam not ended
    if attempt.status == 'submitted':
        return JsonResponse({'error': 'Exam already submitted'}, status=400)
    
    # Allow saving if within duration, even if end_time passed slightly (grace period), 
    # but strict on end_time if it's a fixed schedule.
    # For now, we keep the strict check but return clear error.
    if attempt.exam.end_time < timezone.now():
        return JsonResponse({'error': 'Exam time has ended'}, status=400)
    
    try:
        data = json.loads(request.body)
        question_id = data.get('question_id')
        
        if not question_id:
            return JsonResponse({'error': 'Missing question ID'}, status=400)

        try:
            question = Question.objects.get(id=question_id, exam=attempt.exam)
        except Question.DoesNotExist:
             return JsonResponse({'error': 'Invalid question ID'}, status=400)
        
        selected_choice_id = data.get('selected_choice_id')
        
        # If selected_choice_id is provided, verify it exists and belongs to question
        if selected_choice_id:
            if not question.choices.filter(id=selected_choice_id).exists():
                 # If choice invalid, treat as clearing the answer or error?
                 # Better to return error to debug frontend issues
                 return JsonResponse({'error': 'Invalid choice selection'}, status=400)

        with transaction.atomic():
            # Get or create student answer
            student_answer, created = StudentAnswer.objects.update_or_create(
                attempt=attempt,
                question=question,
                defaults={
                    'selected_choice_id': selected_choice_id,
                    'answer_text': data.get('answer_text', '')
                }
            )
            
            # Update attempt last activity
            attempt.last_activity_at = timezone.now()
            attempt.save(update_fields=['last_activity_at'])
        
        return JsonResponse({
            'success': True,
            'message': 'Answer saved',
            'question_id': question_id,
            'answered_count': attempt.answers.all().count()
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required()
@require_http_methods(["GET"])
def resume_exam(request, attempt_id):
    """
    Resume a previously interrupted exam
    GET: Check if can resume and redirect to take_exam
    """
    attempt = get_object_or_404(ExamAttempt, id=attempt_id)
    
    # Verify ownership
    if attempt.student != request.user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    # Check status
    if attempt.status == 'submitted':
        return render(request, 'exams/exam_already_submitted.html', {
            'attempt': attempt
        })
    
    if attempt.status == 'interrupted':
        # Resume interrupted exam
        attempt.status = 'in_progress'
        attempt.save()
    
    return redirect('dashboards:take_exam', attempt_id=attempt.id)


@login_required()
@require_http_methods(["GET", "POST"])
def submit_exam(request, attempt_id):
    """
    Submit exam - finalize answers and auto-grade objective questions
    GET: Show confirmation page
    POST: Submit and grade
    """
    attempt = get_object_or_404(ExamAttempt, id=attempt_id)
    
    # Verify ownership
    if attempt.student != request.user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    if request.method == 'GET':
        if request.GET.get('confirm') == 'true':
            pass
        else:
            return render(request, 'exams/submit_confirmation.html', {
                'attempt': attempt,
                'answers_count': attempt.answers.all().count(),
                'total_questions': attempt.exam.questions.count()
            })
    
    # POST - Submit exam
    if attempt.status == 'submitted':
        return JsonResponse({
            'error': 'Exam already submitted'
        }, status=400)
    
    with transaction.atomic():
        # Mark all questions as submitted
        attempt.status = 'submitted'
        attempt.completed_at = timezone.now()
        attempt.save()
        
        # Auto-grade objective questions
        objective_questions = attempt.exam.questions.filter(
            type='objective'
        )
        
        total_objective_score = 0
        for question in objective_questions:
            try:
                student_answer = StudentAnswer.objects.get(
                    attempt=attempt,
                    question=question
                )
                
                if student_answer.selected_choice and \
                   student_answer.selected_choice.is_correct:
                    total_objective_score += question.marks
            except StudentAnswer.DoesNotExist:
                pass
        
        # Update attempt with objective score
        attempt.score = total_objective_score
        attempt.save()
        
        # Log system event
        SystemLog.objects.create(
            level='INFO',
            message=f'Student {attempt.student.username} submitted exam: {attempt.exam.title}',
            created_at=timezone.now()
        )
        
        # Create notification for teacher
        if attempt.exam.created_by:
            Notification.objects.create(
                sender=attempt.student,
                recipient=attempt.exam.created_by,
                title='Exam Submitted',
                message=f'{attempt.student.get_full_name()} submitted exam: {attempt.exam.title}',
                related_exam=attempt.exam.id
            )
        
        return redirect('dashboards:exam_result', attempt_id=attempt.id)


@login_required()   
@require_http_methods(["GET"])
def exam_result(request, attempt_id):
    """
    View exam results after submission
    Shows objective score immediately, subjective score when graded
    """
    attempt = get_object_or_404(
        ExamAttempt.objects.select_related('exam', 'student'),
        id=attempt_id
    )
    
    # Verify ownership (student, creator, admin, or parent)
    is_student = (attempt.student == request.user)
    is_creator = (attempt.exam.created_by == request.user)
    is_admin = (request.user.role == User.Role.ADMIN)
    is_parent = (request.user.role == User.Role.PARENT and attempt.student in request.user.children.all())
    
    if not (is_student or is_creator or is_admin or is_parent):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    # Get all answers with grading info
    answers = StudentAnswer.objects.filter(
        attempt=attempt
    ).select_related('question', 'selected_choice')
    
    # Separate objective and subjective
    objective_answers = []
    subjective_answers = []
    answers_breakdown = []
    
    for answer in answers:
        answer_data = {
            'question': answer.question,
            'question_type': answer.question.type,
            'marks': answer.question.marks,
            'marks_for_question': answer.question.marks,
            'answer': answer,
            'answer_text': answer.answer_text,
            'selected_choice': answer.selected_choice,
        }
        
        if answer.question.type == 'objective':
            is_correct = (answer.selected_choice and answer.selected_choice.is_correct)
            answer_data['is_correct'] = is_correct
            answer_data['correct_choice'] = answer.question.choices.filter(
                is_correct=True
            ).first()
            answer_data['marks_obtained'] = answer.question.marks if is_correct else 0
            objective_answers.append(answer_data)
        else:
            # Get grading info if exists
            try:
                grading = SubjectiveMark.objects.get(
                    answer=answer
                )
                answer_data['grading'] = grading
                answer_data['is_graded'] = True
                answer_data['marks_obtained'] = grading.score
            except SubjectiveMark.DoesNotExist:
                answer_data['is_graded'] = False
                answer_data['marks_obtained'] = 0
            
            subjective_answers.append(answer_data)
        
        answers_breakdown.append(answer_data)
    
    return render(request, 'exams/exam_result.html', {
        'attempt': attempt,
        'exam': attempt.exam,
        'objective_answers': objective_answers,
        'subjective_answers': subjective_answers,
        'answers_breakdown': answers_breakdown,
        'objective_score': attempt.score,
        'subjective_score': attempt.subjective_score,
        'total_score': attempt.total_score,
        'total_obtained': attempt.total_score,
        'total_marks': attempt.exam.total_marks,
        'percentage': attempt.percentage,
        'grade': attempt.grade,
        'is_all_graded': attempt.is_fully_graded
        
    })


@login_required()
@require_http_methods(["GET"])
def interrupt_exam(request, attempt_id):
    """
    Interrupt exam - student leaves exam (time remaining > 0)
    Can be resumed later
    """
    attempt = get_object_or_404(ExamAttempt, id=attempt_id)
    
    if attempt.student != request.user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    if attempt.status == 'in_progress':
        attempt.status = 'interrupted'
        attempt.last_activity = timezone.now()
        attempt.save()
        
        SystemLog.objects.create(
            level='INFO',
            message=f'Exam interrupted by {attempt.student.username}: {attempt.exam.title}',
            created_at=timezone.now()
        )
    
    messages.info(request, 'Exam interrupted. You can resume later.')
    return redirect('dashboards:student_available_exams')


# ========================= HELPER FUNCTIONS =========================

def _can_take_exam(student, exam):
    """Check if student has access to exam"""
    # 1. Exam must be published
    if not exam.is_published:
        return False
    
    # 2. If student belongs to the class, they have access
    if exam.school_class == student.student_class:
        return True
    
    # 3. Check if special exam access granted (e.g. mercy, payment, or different class)
    has_access = ExamAccess.objects.filter(
        student=student,
        exam=exam
    ).exists()
    
    return has_access


def _calculate_grade(percentage):
    """Calculate letter grade from percentage"""
    if percentage >= 90:
        return 'A'
    elif percentage >= 80:
        return 'B'
    elif percentage >= 70:
        return 'C'
    elif percentage >= 60:
        return 'D'
    else:
        return 'F'


def _get_time_remaining(attempt):
    """Calculate remaining time in seconds"""
    if attempt.status == 'submitted':
        return 0
    
    elapsed = (timezone.now() - attempt.started_at).total_seconds()
    # Fix: duration field is 'duration', not 'duration_minutes'
    total_seconds = attempt.exam.duration * 60
    return max(0, total_seconds - elapsed)
