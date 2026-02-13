"""
PHASE 3: GRADING & RESULTS INTERFACE
- Subjective answer grading
- Result display with breakdown
- PDF generation
- Charts and analytics
"""

from django.utils.text import slugify
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Count, Avg, F, Sum
from django.utils import timezone
from django.db import transaction
from datetime import datetime, timedelta
import json

# ReportLab imports for PDF
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from io import BytesIO

from accounts.models import User
from exams.models import (
    Exam, ExamAttempt, Question, Choice, StudentAnswer,
    SubjectiveMark, Notification, SystemLog
)


# ========================= TEACHER GRADING VIEWS =========================

@login_required(login_url='login')
@require_http_methods(["GET"])
def teacher_grading_dashboard(request):
    """
    Teacher's grading dashboard - overview of subjective answers
    Shows exams with pending grades
    """
    teacher = request.user
    
    # Get teacher's exams with subjective questions
    all_teacher_exams = Exam.objects.filter(created_by=teacher)
    
    # Annotate exams that have subjective questions
    exams_with_subjective = all_teacher_exams.filter(
        questions__type='subjective'
    ).distinct().annotate(
        total_attempts=Count('exam_attempts', distinct=True, filter=Q(exam_attempts__status='submitted')),
        ungraded_count=Count(
            'exam_attempts__answers',
            distinct=True,
            filter=Q(
                exam_attempts__status='submitted',
                exam_attempts__answers__question__type='subjective',
                exam_attempts__answers__subjective_mark__isnull=True
            )
        )
    ).order_by('-ungraded_count', '-created_at')
    
    context = {
        'exams': exams_with_subjective,
        'total_exams': all_teacher_exams.count(),
        'exams_with_pending': exams_with_subjective.filter(ungraded_count__gt=0).count()
    }
    
    return render(request, 'exams/teacher_grading_dashboard.html', context)


@login_required(login_url='login')
@require_http_methods(["GET"])
def grade_subjective_answers(request, exam_id):
    """
    Grade subjective answers for an exam
    Shows all subjective questions with student answers
    """
    exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)
    teacher = request.user
    
    # Get subjective questions
    subjective_questions = exam.questions.filter(
        type='subjective'
    ).prefetch_related('studentanswer_set')
    
    # Get all exam attempts for this exam
    attempts = ExamAttempt.objects.filter(
        exam=exam,
        status='submitted'
    ).select_related('student')
    
    # Build grading data
    grading_data = []
    for question in subjective_questions:
        question_data = {
            'question': question,
            'answers': []
        }
        
        for attempt in attempts:
            try:
                answer = StudentAnswer.objects.get(
                    attempt=attempt,
                    question=question
                )
                
                # Get grading if exists
                try:
                    grading = SubjectiveMark.objects.get(
                        answer=answer
                    )
                    is_graded = True
                    marks = grading.score
                except SubjectiveMark.DoesNotExist:
                    is_graded = False
                    marks = None
                
                question_data['answers'].append({
                    'answer': answer,
                    'student': attempt.student,
                    'is_graded': is_graded,
                    'marks': marks,
                    'attempt_id': attempt.id
                })
            except StudentAnswer.DoesNotExist:
                pass
        
        grading_data.append(question_data)
    
    return render(request, 'exams/grade_subjective.html', {
        'exam': exam,
        'grading_data': grading_data,
        'total_questions': subjective_questions.count(),
        'total_attempts': attempts.count()
    })


@login_required(login_url='login')
@require_http_methods(["POST"])
def submit_subjective_grade(request):
    """
    Submit grade for a subjective answer (AJAX)
    POST: Save marks
    """
    teacher = request.user
    
    try:
        data = json.loads(request.body)
        answer_id = data.get('answer_id')
        marks = int(data.get('marks', 0))
        
        answer = StudentAnswer.objects.select_related(
            'question', 'attempt'
        ).get(id=answer_id)
        
        # Verify teacher access
        if answer.attempt.exam.created_by != teacher:
            return JsonResponse({
                'error': 'Unauthorized'
            }, status=403)
        
        # Validate marks
        if marks < 0 or marks > answer.question.marks:
            return JsonResponse({
                'error': f'Marks must be between 0 and {answer.question.marks}'
            }, status=400)
        
        with transaction.atomic():
            # Create or update grading
            grading, created = SubjectiveMark.objects.update_or_create(
                answer=answer,
                defaults={
                    'score': marks,
                    'marked_by': teacher,
                    'marked_at': timezone.now()
                }
            )
            
            # Create notification
            Notification.objects.create(
                sender=teacher,
                recipient=answer.attempt.student,
                title='Exam Graded',
                message=f'Your answer to "{answer.question.text[:50]}..." has been graded ({marks}/{answer.question.marks} marks)',
                related_exam=answer.attempt.exam.id
            )
            
            # Log system event
            SystemLog.objects.create(
                level='INFO',
                message=f'{teacher.username} graded subjective answer (attempt {answer.attempt.id})',
                created_at=timezone.now()
            )
        
        return JsonResponse({
            'success': True,
            'message': 'Grade saved',
            'marks': marks,
            'total_score': answer.attempt.total_score,
            'is_all_graded': answer.attempt.is_fully_graded
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


# ========================= RESULT VIEWING VIEWS =========================

@login_required(login_url='login')
@require_http_methods(["GET"])
def student_result_detail(request, attempt_id):
    """
    Student views detailed exam result with breakdown
    Shows objective answers, subjective feedback, overall grade
    """
    attempt = get_object_or_404(
        ExamAttempt.objects.select_related('exam', 'student'),
        id=attempt_id,
        student=request.user
    )
    
    if attempt.status != 'submitted':
        return redirect('dashboards:exam_result', attempt_id=attempt.id)
    
    # Get answers with grading
    answers = StudentAnswer.objects.filter(
        attempt=attempt
    ).select_related('question', 'selected_choice')
    
    # Calculate scores
    objective_score = 0
    subjective_score = 0
    answers_breakdown = []
    
    for answer in answers:
        answer_data = {
            'question': answer.question,
            'answer_text': answer.answer_text,
            'selected_choice': answer.selected_choice,
            'marks_for_question': answer.question.marks,
            'question_type': answer.question.type
        }
        
        if answer.question.type == 'objective':
            is_correct = answer.selected_choice and answer.selected_choice.is_correct
            answer_data['is_correct'] = is_correct
            answer_data['marks_obtained'] = answer.question.marks if is_correct else 0
            answer_data['correct_choice'] = answer.question.choices.filter(
                is_correct=True
            ).first()
            objective_score += answer_data['marks_obtained']
        else:
            # Get subjective grading
            try:
                grading = SubjectiveMark.objects.get(answer=answer)
                answer_data['marks_obtained'] = grading.score
                answer_data['is_graded'] = True
                subjective_score += grading.score
            except SubjectiveMark.DoesNotExist:
                answer_data['marks_obtained'] = 0
                answer_data['is_graded'] = False
        
        answers_breakdown.append(answer_data)
    
    # Calculate total
    total_marks = attempt.exam.total_marks
    total_obtained = objective_score + subjective_score
    percentage = attempt.percentage
    
    return render(request, 'exams/student_result_detail.html', {
        'attempt': attempt,
        'answers_breakdown': answers_breakdown,
        'objective_score': objective_score,
        'subjective_score': subjective_score,
        'total_obtained': total_obtained,
        'total_marks': total_marks,
        'percentage': percentage,
        'grade': attempt.grade,
        'is_all_graded': attempt.is_fully_graded
    })


@login_required(login_url='login')
@require_http_methods(["GET"])
def parent_child_result(request, attempt_id):
    """
    Parent views their child's exam result
    Shows overall performance and feedback
    """
    attempt = get_object_or_404(
        ExamAttempt.objects.select_related('exam', 'student'),
        id=attempt_id,
        status='submitted'
    )
    
    # Verify parent access
    if attempt.student not in request.user.children.all():
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    # Get performance data
    student_answers = StudentAnswer.objects.filter(
        attempt=attempt
    ).select_related('question')
    
    objective_correct = 0
    objective_total = 0
    subjective_graded = 0
    subjective_pending = 0
    
    for answer in student_answers:
        if answer.question.type == 'objective':
            objective_total += 1
            if answer.selected_choice and answer.selected_choice.is_correct:
                objective_correct += 1
        else:
            try:
                SubjectiveMark.objects.get(answer=answer)
                subjective_graded += 1
            except SubjectiveMark.DoesNotExist:
                subjective_pending += 1
    
    # Calculate overall performance
    performance = {
        'objective_correct': objective_correct,
        'objective_total': objective_total,
        'objective_percentage': (objective_correct / objective_total * 100) if objective_total > 0 else 0,
        'subjective_graded': subjective_graded,
        'subjective_pending': subjective_pending,
        'total_score': attempt.total_score,
        'percentage': attempt.percentage
    }
    
    return render(request, 'exams/parent_child_result.html', {
        'attempt': attempt,
        'child': attempt.student,
        'performance': performance,
        'feedback_pending': subjective_pending > 0
    })


# ========================= PDF GENERATION =========================

@login_required(login_url='login')
@require_http_methods(["GET"])
def download_result_pdf(request, attempt_id):
    """
    Generate and download exam result as PDF
    Shows complete answer sheet with marks
    """
    attempt = get_object_or_404(
        ExamAttempt.objects.select_related('exam', 'student'),
        id=attempt_id
    )
    
    # Verify access
    is_student = (attempt.student == request.user)
    is_creator = (attempt.exam.created_by == request.user)
    is_admin = (request.user.role == User.Role.ADMIN)

    if not (is_student or is_creator or is_admin):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    # Create PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=12,
        alignment=1  # Center
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#333333'),
        spaceAfter=6,
        spaceBefore=12
    )
    
    # Header
    elements.append(Paragraph('EXAM RESULT SHEET', title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Student Info
    student_info = [
        ['Student Name:', attempt.student.get_full_name()],
        ['Exam:', attempt.exam.title],
        ['Class:', str(attempt.student.student_class)],
        ['Date:', attempt.completed_at.strftime('%d-%m-%Y %H:%M') if attempt.completed_at else 'N/A'],
    ]
    
    info_table = Table(student_info, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e6f2ff')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Answers
    elements.append(Paragraph('ANSWER BREAKDOWN', heading_style))
    
    answers = StudentAnswer.objects.filter(
        attempt=attempt
    ).select_related('question', 'selected_choice').order_by(
        'question__order'
    )
    
    answer_data = [['Q#', 'Type', 'Marks', 'Status']]
    
    for i, answer in enumerate(answers, 1):
        qtype = 'Objective' if answer.question.type == 'objective' else 'Subjective'
        
        if answer.question.type == 'objective':
            is_correct = answer.selected_choice and answer.selected_choice.is_correct
            marks = answer.question.marks if is_correct else 0
            status = '✓ Correct' if is_correct else '✗ Incorrect'
        else:
            try:
                grading = SubjectiveMark.objects.get(answer=answer)
                marks = grading.score
                status = f'{marks}/{answer.question.marks}'
            except SubjectiveMark.DoesNotExist:
                marks = 0
                status = 'Pending'
        
        answer_data.append([str(i), qtype, str(marks), status])
    
    answer_table = Table(answer_data, colWidths=[0.5*inch, 1.5*inch, 1*inch, 2.5*inch])
    answer_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
    ]))
    
    elements.append(answer_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Score Summary
    total_marks = attempt.exam.total_marks
   
    percentage = attempt.percentage
    
    score_data = [
        ['Objective Score:', f'{attempt.score or 0}'],
        ['Subjective Score:', f'{attempt.subjective_score or 0}'],
        ['Total Score:', f'{attempt.total_score}'],
        ['Total Marks:', str(total_marks)],
        ['Percentage:', f'{percentage:.1f}%'],
        ['Grade:', _calculate_grade(percentage)]
    ]
    
    score_table = Table(score_data, colWidths=[3*inch, 2.5*inch])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e6f2ff')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    
    elements.append(score_table)
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    # Return as attachment
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{slugify(attempt.exam.title)}_{attempt.student.username}_result.pdf"'
    
    return response


# ========================= ANALYTICS & CHARTS =========================

@login_required(login_url='login')
@require_http_methods(["GET"])
def exam_analytics(request, exam_id):
    """
    View analytics for an exam - grades distribution, question performance
    """
    exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)
    
    # Get all attempts
    attempts = ExamAttempt.objects.filter(
        exam=exam,
        status='submitted'
    ).select_related('student')
    
    # Calculate statistics
    if attempts.exists():
        stats = attempts.aggregate(
            total_attempts=Count('id'),
            avg_score=Avg('total_score'),
            max_score=F('total_score'),
            min_score=F('total_score')
        )
        
        # Get grade distribution
        grades = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
        total_marks = exam.total_marks
        
        for attempt in attempts:
            percentage = attempt.percentage
            grade = _calculate_grade(percentage)
            grades[grade] += 1
        
        # Question performance
        questions_perf = []
        for question in exam.questions.all():
            answers = StudentAnswer.objects.filter(
                attempt__in=attempts,
                question=question
            )
            
            if question.type == 'objective':
                correct = sum(
                    1 for a in answers
                    if a.selected_choice and a.selected_choice.is_correct
                )
                success_rate = (correct / answers.count() * 100) if answers.count() > 0 else 0
            else:
                graded = SubjectiveMark.objects.filter(
                    student_answer__in=answers
                ).count()
                success_rate = (graded / answers.count() * 100) if answers.count() > 0 else 0
            
            questions_perf.append({
                'question': question,
                'attempt_count': answers.count(),
                'success_rate': success_rate
            })
    else:
        stats = {
            'total_attempts': 0,
            'avg_score': 0,
            'max_score': 0,
            'min_score': 0
        }
        grades = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
        questions_perf = []
    
    return render(request, 'exams/exam_analytics.html', {
        'exam': exam,
        'stats': stats,
        'grades': grades,
        'questions_performance': questions_perf,
        'total_attempts': len(attempts),
        'grade_distribution_json': json.dumps(grades),
        'attempts': attempts.order_by('-submitted_at')[:10]  # Latest 10
    })


# ========================= HELPER FUNCTIONS =========================

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
