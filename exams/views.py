import re
import openpyxl
from docx import Document
from .models import Exam, Question, Choice
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404
from .models import ExamAttempt, StudentAnswer
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from .models import Exam, ExamAttempt, StudentAnswer, SubjectiveMark, Choice, SchoolClass, RetakeRequest, Notification, PTARequest, Question
from django.db import transaction
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count
from django.shortcuts import render, redirect
from django.utils import timezone
from exams.models import Exam, ExamAttempt, StudentAnswer
from accounts.models import User
from django.db.models import Sum, Avg, F    
from brillspay.models import PaymentTransaction
from pickup.models import PickupAuthorization
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db.models import Sum, Count
from brillspay.models import Order
from exams.models import Exam, ExamAttempt
from django.utils.timezone import now
from datetime import timedelta



import logging
logger = logging.getLogger("system")

def teacher_required(user):
    return user.is_authenticated and user.role == 'STAFF'


def cbt_exam(request):
    return render(request, 'exams/home.html')

@login_required
@user_passes_test(teacher_required)
def create_exam(request):
    if request.method == 'POST':
        Exam.objects.create(
            title=request.POST['title'],
            school_class_id=request.POST['school_class'],
            duration=request.POST['duration'],
            start_time=request.POST['start_time'],
            end_time=request.POST['end_time'],
            created_by=request.user,
            is_published=False  # 🔒 FORCE DRAFT
        )
        return redirect('teacher_exam_list')

    return render(request, 'exams/teacher/create_exam.html')

@login_required
@user_passes_test(teacher_required)
def question_list(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)
    questions = Question.objects.filter(exam=exam)
    return render(request, 'exams/teacher/question_list.html', {
        'exam': exam,
        'questions': questions
    })


@login_required
@user_passes_test(teacher_required)
def add_question(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)

    if request.method == 'POST':
        q_type = request.POST['type']

        question = Question.objects.create(
            exam=exam,
            text=request.POST['text'],
            type=q_type,
            marks=request.POST['marks']
        )

        # Objective only → create choices
        if q_type == 'objective':
            correct = request.POST.get('correct')

            for key in ['A', 'B', 'C', 'D']:
                Choice.objects.create(
                    question=question,
                    text=request.POST.get(key),
                    is_correct=(key == correct)
                )

        messages.success(request, "Question added successfully.")
        return redirect('question_list', exam_id=exam.id)

    return render(request, 'exams/teacher/add_question.html', {'exam': exam})



@login_required
@user_passes_test(teacher_required)
def teacher_exam_list(request):
    exams = Exam.objects.filter(created_by=request.user)
    return render(request, 'exams/teacher/exam_list.html', {'exams': exams})


def admin_required(user):
    return user.is_authenticated and user.role == 'ADMIN'


@login_required
@user_passes_test(admin_required)
def admin_exam_list(request):
    exams = Exam.objects.select_related('school_class', 'created_by')
    return render(request, 'exams/admin/exam_list.html', {'exams': exams})


@login_required
@user_passes_test(admin_required)
def toggle_exam_publish(request, pk):
    exam = Exam.objects.get(pk=pk)
    exam.is_published = not exam.is_published
    exam.save(update_fields=['is_published'])
    return redirect('admin_exam_list')



@staff_member_required
def admin_toggle_retake(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    exam.allow_retake = not exam.allow_retake
    exam.save(update_fields=["allow_retake"])

    messages.success(request, "Retake setting updated")
    return redirect("exams:admin_exam_list")



@login_required
@user_passes_test(teacher_required)
def upload_questions_excel(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)

    if request.method == 'POST':
        file = request.FILES.get('file')

        if not file or not file.name.endswith('.xlsx'):
            messages.error(request, "Upload a valid Excel (.xlsx) file.")
            return redirect('question_list', exam.id)

        wb = openpyxl.load_workbook(file)
        sheet = wb.active

        errors = []
        created = 0

        with transaction.atomic():
            for idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
                text, qtype, marks, A, B, C, D, correct = row

                if not text or not qtype or not marks:
                    errors.append(f"Row {idx}: Missing required fields")
                    continue

                qtype = qtype.lower().strip()

                if qtype not in ['objective', 'subjective']:
                    errors.append(f"Row {idx}: Invalid type")
                    continue

                question = Question.objects.create(
                    exam=exam,
                    text=text,
                    type=qtype,
                    marks=int(marks)
                )

                if qtype == 'objective':
                    if not all([A, B, C, D, correct]):
                        errors.append(f"Row {idx}: Objective missing options")
                        raise Exception("Invalid objective row")

                    for key, value in zip(['A','B','C','D'], [A,B,C,D]):
                        Choice.objects.create(
                            question=question,
                            text=value,
                            is_correct=(key == correct)
                        )

                created += 1

            if errors:
                raise Exception("Validation failed")

        messages.success(request, f"{created} questions uploaded successfully.")
        return redirect('question_list', exam.id)

    return render(request, 'exams/teacher/upload_excel.html', {'exam': exam})


@login_required
@user_passes_test(teacher_required)
def upload_questions_word(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)

    if request.method == 'POST':
        file = request.FILES.get('file')
        if not file or not file.name.endswith('.docx'):
            messages.error(request, "Please upload a valid .docx file.")
            return redirect('question_list', exam.id)

        doc = Document(file)
        questions_text = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

        errors = []
        created = 0

        with transaction.atomic():
            i = 0
            while i < len(questions_text):
                line = questions_text[i]

                # Match: 1. Question text [Type] [Marks: N]
                m = re.match(r'^\d+\.\s+(.*?)\s+\[(objective|subjective)\]\s+\[Marks:\s*(\d+)\]$', line, re.I)
                if not m:
                    errors.append(f"Line {i+1} invalid format")
                    i += 1
                    continue

                text, qtype, marks = m.groups()
                qtype = qtype.lower()
                marks = int(marks)
                i += 1

                question = Question.objects.create(
                    exam=exam,
                    text=text,
                    type=qtype,
                    marks=marks
                )

                # Objective → next 4 lines = options A-D + Answer line
                if qtype == 'objective':
                    if i + 4 >= len(questions_text):
                        errors.append(f"Question '{text}' incomplete options")
                        break

                    options = []
                    for letter in ['A','B','C','D']:
                        option_line = questions_text[i]
                        if not option_line.startswith(letter+'.'):
                            errors.append(f"Expected option {letter} for '{text}'")
                            break
                        options.append(option_line[2:].strip())
                        i += 1

                    # Answer line
                    answer_line = questions_text[i]
                    m2 = re.match(r'^Answer:\s*([A-D])$', answer_line, re.I)
                    if not m2:
                        errors.append(f"Answer missing for '{text}'")
                        i += 1
                        continue
                    correct = m2.group(1).upper()
                    i += 1

                    # Save choices
                    for letter, opt in zip(['A','B','C','D'], options):
                        Choice.objects.create(
                            question=question,
                            text=opt,
                            is_correct=(letter == correct)
                        )

                created += 1

        if errors:
            messages.warning(request, f"{created} questions uploaded, {len(errors)} errors.")
        else:
            messages.success(request, f"{created} questions uploaded successfully.")

        return redirect('question_list', exam.id)

    return render(request, 'exams/teacher/upload_word.html', {'exam': exam})


from django.utils import timezone

@login_required
def exam_list(request):
    # Only published, active exams, and not ended
    exams = Exam.objects.filter(
        is_published=True,
        is_active=True,
        start_time__lte=timezone.now(),
        end_time__gte=timezone.now()
    ).order_by('start_time')
    
    # Optionally, filter out already submitted exams unless allow_retake
    return render(request, 'exams/student/exam_list.html', {'exams': exams})



@login_required
def start_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id, is_published=True)
    user = request.user
    if exam.requires_payment:
        if not has_paid_for_exam(request.user, exam):
            messages.warning(request, "Payment required to access this exam")
            return redirect("brillspay:exam_checkout", exam.id)

    # Check if already started
    attempt = ExamAttempt.objects.filter(exam=exam, student=user, is_submitted=False).first()
    if attempt:
        return redirect('exams:resume_exam', attempt_id=attempt.id)

    # Start new attempt
    attempt = ExamAttempt.objects.create(
        exam=exam,
        student=user,
        retake_allowed=exam.allow_retake
    )

    # Record question order
    question_ids = list(exam.question_set.values_list('id', flat=True))
    import random
    random.shuffle(question_ids)
    attempt.question_order = ','.join(str(q) for q in question_ids)
    attempt.save()

    return redirect('resume_exam', attempt_id=attempt.id)


@login_required
def resume_exam(request, attempt_id):
    attempt = get_object_or_404(ExamAttempt, id=attempt_id, student=request.user)
    exam = attempt.exam

    # Calculate remaining time
    start = attempt.started_at
    elapsed = (timezone.now() - start).total_seconds() / 60
    remaining = exam.duration - elapsed

    if remaining <= 0:
        attempt.is_submitted = True
        attempt.completed_at = timezone.now()
        attempt.save()
        messages.info(request, "Time is up!")
        return redirect('exam_list')

    question_ids = [int(qid) for qid in attempt.question_order.split(',')]
    questions = Question.objects.filter(id__in=question_ids)

    if request.method == 'POST':
        for q in questions:
            ans_text = request.POST.get(f'answer_{q.id}', '').strip()
            selected_choice_id = request.POST.get(f'choice_{q.id}')
            choice = Choice.objects.filter(id=selected_choice_id).first() if selected_choice_id else None

            StudentAnswer.objects.update_or_create(
                attempt=attempt,
                question=q,
                defaults={'answer_text': ans_text, 'selected_choice': choice}
            )

        if 'submit' in request.POST:
            attempt.is_submitted = True
            attempt.completed_at = timezone.now()
            attempt.save()
            auto_grade_objective(attempt)
            messages.success(request, "Exam submitted successfully!")
            return redirect('exam_list')

        messages.info(request, "Progress saved. Continue the exam.")

    return render(request, 'exams/student/resume_exam.html', {
        'exam': exam,
        'attempt': attempt,
        'questions': questions,
        'remaining': int(remaining*60)  # seconds
    })


def auto_grade_objective(attempt):
    for ans in StudentAnswer.objects.filter(attempt=attempt):
        if ans.question.type == 'objective':
            if ans.selected_choice and ans.selected_choice.is_correct:
                # For simplicity, store marks in answer_text temporarily
                ans.answer_text = f"Correct ({ans.question.marks})"
            else:
                ans.answer_text = "Incorrect (0)"
            ans.save()




@login_required
@user_passes_test(teacher_required)
def subjective_marking(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    attempts = ExamAttempt.objects.filter(exam=exam, is_submitted=True)

    if request.method == 'POST':
        with transaction.atomic():
            for key, value in request.POST.items():
                if key.startswith('mark_'):
                    ans_id = int(key.split('_')[1])
                    ans = StudentAnswer.objects.get(id=ans_id)
                    score = int(value)
                    SubjectiveMark.objects.update_or_create(
                        answer=ans,
                        defaults={'score': score, 'marked_by': request.user}
                    )
        messages.success(request, "Marks saved successfully!")
        return redirect('subjective_marking', exam_id=exam.id)

    # Gather all unmarked subjective answers
    answers = StudentAnswer.objects.filter(
        attempt__exam=exam,
        question__type='subjective'
    ).select_related('attempt', 'question').order_by('attempt__student__username')

    return render(request, 'exams/teacher/subjective_marking.html', {
        'exam': exam,
        'answers': answers
    })


@login_required
def student_results(request):
    attempts = ExamAttempt.objects.filter(student=request.user, is_submitted=True).select_related('exam')
    results = []

    for attempt in attempts:
        total_marks = 0
        obtained = 0

        for ans in attempt.studentanswer_set.all():
            if ans.question.type == 'objective':
                if ans.selected_choice and ans.selected_choice.is_correct:
                    obtained += ans.question.marks
                total_marks += ans.question.marks
            elif ans.question.type == 'subjective':
                mark = getattr(ans, 'subjectivemark', None)
                obtained += mark.score if mark else 0
                total_marks += ans.question.marks

        results.append({
            'exam': attempt.exam,
            'obtained': obtained,
            'total': total_marks
        })

    return render(request, 'exams/student/results.html', {'results': results})


@login_required
@user_passes_test(teacher_required)
def class_leaderboard(request, class_id):
    school_class = get_object_or_404(SchoolClass, id=class_id)
    students = school_class.students.all()
    leaderboard = []

    for student in students:
        attempts = ExamAttempt.objects.filter(student=student, is_submitted=True)
        total_obtained = 0
        total_marks = 0
        for attempt in attempts:
            for ans in attempt.studentanswer_set.all():
                if ans.question.type == 'objective':
                    if ans.selected_choice and ans.selected_choice.is_correct:
                        total_obtained += ans.question.marks
                    total_marks += ans.question.marks
                elif ans.question.type == 'subjective':
                    mark = getattr(ans, 'subjectivemark', None)
                    total_obtained += mark.score if mark else 0
                    total_marks += ans.question.marks

        leaderboard.append({
            'student': student,
            'score': total_obtained,
            'total': total_marks,
            'percentage': (total_obtained/total_marks*100) if total_marks>0 else 0
        })

    leaderboard.sort(key=lambda x: x['score'], reverse=True)

    return render(request, 'exams/teacher/leaderboard.html', {
        'class': school_class,
        'leaderboard': leaderboard
    })


@login_required
def request_retake(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    user = request.user

    existing = RetakeRequest.objects.filter(student=user, exam=exam).first()
    if request.method == 'POST':
        reason = request.POST.get('reason')
        if not existing:
            RetakeRequest.objects.create(student=user, exam=exam, reason=reason)
        else:
            messages.info(request, "You already requested a retake.")
        messages.success(request, "Retake request submitted.")
        return redirect('exam_list')

    return render(request, 'exams/student/request_retake.html', {'exam': exam})


@login_required
@user_passes_test(admin_required)
def manage_retake(request):
    requests = RetakeRequest.objects.filter(status='pending')

    if request.method == 'POST':
        for key, value in request.POST.items():
            if key.startswith('action_'):
                rid = int(key.split('_')[1])
                action = value
                r = RetakeRequest.objects.get(id=rid)
                r.status = action
                r.reviewed_by = request.user
                r.reviewed_at = timezone.now()
                r.save()
        messages.success(request, "Retake requests updated.")
        return redirect('manage_retake')

    return render(request, 'exams/admin/manage_retake.html', {'requests': requests})


@login_required
def notifications_list(request):
    user = request.user
    notifications = user.notifications.all()
    return render(request, 'exams/notifications/list.html', {'notifications': notifications})

@login_required
def mark_notification_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notif.mark_read()
    return JsonResponse({'status': 'ok'})


@login_required
@user_passes_test(teacher_required)
def send_broadcast(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        students = settings.AUTH_USER_MODEL.objects.filter(role='STUDENT')
        for s in students:
            Notification.objects.create(sender=request.user, recipient=s,
                                        title="Teacher Broadcast", message=message)
        messages.success(request, "Broadcast sent.")
        return redirect('send_broadcast')

    return render(request, 'exams/notifications/broadcast.html')


@login_required
def take_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    user = request.user
    exam = get_object_or_404(Exam, id=exam_id, is_published=True)

    if exam.requires_payment:
        if not has_paid_for_exam(request.user, exam):
            messages.warning(request, "Payment required to access this exam")
            return redirect("brillspay:exam_checkout", exam.id)



    # Check active window
    now = timezone.now()
    if now < exam.start_time or now > exam.end_time:
        messages.warning(request, "Exam is not active.")
        return redirect('student_dashboard')

    # Get existing attempt or create new
    attempt, created = ExamAttempt.objects.get_or_create(
        exam=exam, student=user,
        defaults={'remaining_seconds': exam.duration * 60}
    )

    # Resume remaining time
    if request.method == 'POST':
        # Save answers asynchronously via JS (fetch)
        pass  # we'll handle AJAX later

    questions = list(exam.question_set.all())
    return render(request, 'exams/student/take_exam.html', {
        'exam': exam,
        'attempt': attempt,
        'questions': questions
    })



@login_required
def submit_exam(request, attempt_id):
    """
    Handles submission of an exam attempt.
    - Saves objective answers and auto-grades
    - Saves subjective answers for teacher grading
    - Marks the attempt as submitted
    """
    attempt = get_object_or_404(ExamAttempt, id=attempt_id, student=request.user)
    exam = attempt.exam

    if attempt.is_submitted:
        messages.warning(request, "This exam has already been submitted.")
        return redirect('student_dashboard')

    if request.method == 'POST':
        # Iterate over all questions
        for question in exam.question_set.all():
            answer_text = request.POST.get(f'q{question.id}', '').strip()
            selected_choice_id = request.POST.get(f'q{question.id}_choice', None)

            # Save or update StudentAnswer
            sa, created = StudentAnswer.objects.get_or_create(
                attempt=attempt, question=question
            )
            sa.answer_text = answer_text

            if question.type == 'objective' and selected_choice_id:
                choice = get_object_or_404(Choice, id=selected_choice_id)
                sa.selected_choice = choice

            sa.save()

            # Auto-grade objective questions
            if question.type == 'objective' and sa.selected_choice:
                score = question.marks if sa.selected_choice.is_correct else 0
                SubjectiveMark.objects.update_or_create(
                    answer=sa,
                    defaults={'score': score, 'marked_by': request.user}
                )

        # Mark attempt as submitted
        attempt.is_submitted = True
        attempt.completed_at = timezone.now()
        attempt.save()

        messages.success(request, "Exam submitted successfully!")
        return redirect('student_dashboard')

    # Fallback: redirect if not POST
    return redirect('take_exam', exam_id=exam.id)



@login_required
def save_exam_progress(request, attempt_id):
    attempt = get_object_or_404(ExamAttempt, id=attempt_id, student=request.user)
    if request.method == 'POST':
        remaining = int(request.POST.get('remaining_seconds', 0))
        attempt.save_progress(remaining)
        return JsonResponse({'status': 'ok'})


@login_required
def auto_submit_exam(request, attempt_id):
    attempt = get_object_or_404(ExamAttempt, id=attempt_id, student=request.user)
    if request.method == 'POST':
        attempt.is_submitted = True
        attempt.completed_at = timezone.now()
        attempt.save()
        return JsonResponse({'status': 'submitted'})


@login_required
def check_notifications(request):
    user = request.user
    new_notifs = user.notifications.filter(is_read=False).values('id', 'title', 'message', 'created_at')
    return JsonResponse({'notifications': list(new_notifs)})

@login_required
@user_passes_test(lambda u: u.is_superuser or u.role=='ADMIN')
def approve_retake(request, retake_id):
    retake = get_object_or_404(RetakeRequest, id=retake_id)
    retake.status = 'approved'
    retake.reviewed_at = timezone.now()
    retake.reviewed_by = request.user
    retake.save()

    # Allow exam retake
    attempt, created = ExamAttempt.objects.get_or_create(
        student=retake.student,
        exam=retake.exam
    )
    attempt.retake_allowed = True
    attempt.remaining_seconds = retake.exam.duration * 60
    attempt.is_submitted = False
    attempt.save()

    # Send notification
    Notification.objects.create(
        recipient=retake.student,
        title="Retake Approved",
        message=f"Your retake for exam '{retake.exam.title}' has been approved. You can resume now!"
    )

    messages.success(request, f"Retake approved for {retake.student.username}")
    return redirect('retake_requests_list')


@login_required
def teacher_grading_dashboard(request):
    user = request.user
    if user.role != 'STAFF':
        messages.error(request, "Access denied.")
        return redirect('home')

    # Fetch all subjective answers for exams created by this teacher
    answers = StudentAnswer.objects.filter(
        question__exam__created_by=user,
        question__type='subjective',
        attempt__is_submitted=True
    ).select_related('question', 'attempt__student')

    return render(request, 'exams/teacher/grading_dashboard.html', {
        'answers': answers
    })


from django.http import JsonResponse

@login_required
def save_subjective_mark(request, answer_id):
    user = request.user
    answer = get_object_or_404(StudentAnswer, id=answer_id)

    if user.role != 'STAFF':
        return JsonResponse({'status':'error','msg':'Access denied'}, status=403)

    if request.method == 'POST':
        score = request.POST.get('score')
        try:
            score = int(score)
            SubjectiveMark.objects.update_or_create(
                answer=answer,
                defaults={'score': score, 'marked_by': user}
            )
            return JsonResponse({'status':'ok','score':score})
        except ValueError:
            return JsonResponse({'status':'error','msg':'Invalid score'})
    return JsonResponse({'status':'error','msg':'Invalid request'})


from django.db.models import Sum, Q
from exams.models import ExamAttempt, SubjectiveMark

def get_student_performance(student):
    """
    Returns performance labels (subjects) and scores for Chart.js
    """
    # Fetch all completed attempts for this student
    attempts = ExamAttempt.objects.filter(student=student, is_submitted=True)
    
    labels = []
    scores = []

    for attempt in attempts:
        exam = attempt.exam
        # Sum objective + subjective marks
        objective_marks = SubjectiveMark.objects.filter(
            answer__attempt=attempt,
            answer__question__type='objective'
        ).aggregate(total=Sum('score'))['total'] or 0

        subjective_marks = SubjectiveMark.objects.filter(
            answer__attempt=attempt,
            answer__question__type='subjective'
        ).aggregate(total=Sum('score'))['total'] or 0

        total_score = objective_marks + subjective_marks

        labels.append(exam.title)
        scores.append(total_score)
    
    return labels, scores


def get_class_leaderboard(school_class):
    """
    Returns list of students with total scores, sorted by score descending
    """
    students = school_class.students.filter(is_active=True)
    leaderboard = []

    for student in students:
        attempts = ExamAttempt.objects.filter(student=student, exam__school_class=school_class, is_submitted=True)
        total_score = SubjectiveMark.objects.filter(answer__attempt__in=attempts).aggregate(total=Sum('score'))['total'] or 0
        leaderboard.append({'student': student, 'total_score': total_score})

    leaderboard = sorted(leaderboard, key=lambda x: x['total_score'], reverse=True)
    # Add ranks
    for i, entry in enumerate(leaderboard, start=1):
        entry['rank'] = i
    return leaderboard


@login_required
def fetch_messages(request):
    user = request.user
    messages = PTARequest.objects.filter(
        Q(recipient=user) | Q(parent=user)
    ).order_by('-created_at')[:20]  # last 20 messages
    data = [{
        'id': m.id,
        'title': m.title,
        'message': m.message,
        'created_at': m.created_at.isoformat(),
        'status': m.status,
    } for m in messages]
    return JsonResponse({'messages': data})


@login_required
@csrf_exempt
def mark_message_read(request, message_id):
    m = get_object_or_404(PTARequest, id=message_id, recipient=request.user)
    m.status = 'RESOLVED'
    m.save()
    return JsonResponse({'status':'ok'})



@login_required
def parent_dashboard(request):
    user = request.user

    if user.role != 'PARENT':
        return redirect('accounts:login')

    children = user.children.select_related('student_class')

    pta_requests = PTARequest.objects.filter(parent=user).order_by('-created_at')[:5]

    notifications = Notification.objects.filter(
        recipient=user, is_read=False
    )[:5]

    return render(request, 'parent/dashboard.html', {
        'children': children,
        'pta_requests': pta_requests,
        'notifications': notifications,
    })




@login_required
def teacher_dashboard(request):
    user = request.user

    if user.role != 'STAFF':
        return redirect('login')

    exams = Exam.objects.filter(created_by=user).order_by('-created_at')

    pending_marking = StudentAnswer.objects.filter(
        question__exam__created_by=user,
        question__type='subjective',
        subjectivemark__isnull=True,
        attempt__is_submitted=True
    ).count()

    notifications = Notification.objects.filter(
        recipient=user, is_read=False
    )[:5]

    return render(request, 'teachers/dashboard.html', {
        'exams': exams,
        'pending_marking': pending_marking,
        'notifications': notifications,
    })




def is_admin(user):
    return user.is_authenticated and user.role == "ADMIN"


@login_required
def student_dashboard(request):
    if request.user.role != "STUDENT":
        return redirect("login")

    # Available exams (active + published)
    available_exams = Exam.objects.filter(
        school_class=request.user.student_class,
        is_active=True,
        is_published=True,
        start_time__lte=timezone.now(),
        end_time__gte=timezone.now()
    )

    # Student attempts
    attempts = ExamAttempt.objects.filter(student=request.user)

    # Completed exams and marks
    results = []
    for attempt in attempts.filter(is_submitted=True):
        total_score = StudentAnswer.objects.filter(
            attempt=attempt
        ).aggregate(Sum('score'))['score__sum'] or 0
        results.append({
            "exam": attempt.exam,
            "score": total_score,
            "completed_at": attempt.completed_at
        })

    # Leaderboard for class
    leaderboard = (
        User.objects.filter(student_class=request.user.student_class, role="STUDENT")
        .annotate(total_marks=Sum('studentattempt__score'))
        .order_by('-total_marks')[:10]
    )

    return render(request, "student/dashboard.html", {
        "available_exams": available_exams,
        "attempts": attempts,
        "results": results,
        "leaderboard": leaderboard
    })


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    context = {
        # USERS
        "pending_users": User.objects.filter(is_approved=False).count(),
        "students": User.objects.filter(role="STUDENT").count(),
        "parents": User.objects.filter(role="PARENT").count(),
        "staff": User.objects.filter(role="STAFF").count(),

        # EXAMS
        "active_exams": Exam.objects.filter(is_active=True).count(),
        "unpublished_exams": Exam.objects.filter(is_published=False).count(),
        "retake_requests": RetakeRequest.objects.filter(status="pending").count(),

        # PAYMENTS
        "total_transactions": PaymentTransaction.objects.count(),
        "successful_payments": PaymentTransaction.objects.filter(status="success").count(),

        # PICKUPS
        "active_pickups": PickupAuthorization.objects.filter(
            expires_at__gt=timezone.now(),
            is_used=False
        ).count(),
        
        # PTA
        "pending_pta": PTARequest.objects.filter(status="PENDING").count(),

        # SYSTEM LOGS
        "system_errors": SystemLog.objects.filter(level="ERROR").count(),
       
    }

    return render(request, "exams/admin/dashboard.html", context)


@staff_member_required
def admin_analytics_dashboard(request):
    # Revenue (last 30 days)
    last_30 = now() - timedelta(days=30)

    revenue_qs = (
        Order.objects.filter(is_paid=True, created_at__gte=last_30)
        .values("created_at__date")
        .annotate(total=Sum("total"))
        .order_by("created_at__date")
    )

    revenue_labels = [str(r["created_at__date"]) for r in revenue_qs]
    revenue_data = [float(r["total"]) for r in revenue_qs]

    # Exams stats
    total_exams = Exam.objects.count()
    published_exams = Exam.objects.filter(is_published=True).count()
    attempts = ExamAttempt.objects.count()
    completed = ExamAttempt.objects.filter(is_submitted=True).count()

    context = {
        "revenue_labels": revenue_labels,
        "revenue_data": revenue_data,
        "total_exams": total_exams,
        "published_exams": published_exams,
        "attempts": attempts,
        "completed": completed,
    }
    return render(request, "admin/analytics/dashboard.html", context)



from django.shortcuts import redirect
from django.contrib import messages
from .utils import has_paid_for_exam
from exams.models import Exam, ExamAccessOverride, Broadcast, PTARequest



@staff_member_required
def grant_exam_access(request):
    if request.method == "POST":
        ExamAccessOverride.objects.create(
            student_id=request.POST["student"],
            exam_id=request.POST["exam"],
            reason=request.POST.get("reason", ""),
            granted_by=request.user
        )
        messages.success(request, "Exam access granted")
        return redirect("admin:grant_exam_access")

    context = {
        "students": User.objects.filter(role="STUDENT"),
        "exams": Exam.objects.all()
    }
    return render(request, "admin/exams/grant_access.html", context)


@login_required
def teacher_exam_analytics(request):
    exams = Exam.objects.filter(created_by=request.user)

    analytics = []
    for exam in exams:
        attempts = ExamAttempt.objects.filter(exam=exam)
        completed = attempts.filter(is_submitted=True)

        analytics.append({
            "exam": exam,
            "total_attempts": attempts.count(),
            "completed": completed.count(),
            "avg_score": completed.aggregate(
                avg=Avg("studentanswer__subjectivemark__score")
            )["avg"] or 0,
            "pending_marking": StudentAnswer.objects.filter(
                question__exam=exam,
                question__type="subjective",
                subjectivemark__isnull=True
            ).count()
        })

    return render(
        request,
        "teachers/analytics/dashboard.html",
        {"analytics": analytics}
    )


@staff_member_required
def communication_analytics(request):
    pta_stats = (
        PTARequest.objects
        .values("status")
        .annotate(count=Count("id"))
    )

    broadcasts = Broadcast.objects.aggregate(
        total=Count("id"),
        read=Count("read_by")
    )

    return render(request, "admin/analytics/communication.html", {
        "pta_stats": pta_stats,
        "broadcasts": broadcasts
    })

from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.shortcuts import render
from .models import SystemLog


@staff_member_required
def system_logs(request):
    logs = SystemLog.objects.all()

    level = request.GET.get("level")
    if level:
        logs = logs.filter(level=level)

    paginator = Paginator(logs, 50)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "admin/system_logs/logs.html",
        {
            "logs": page_obj,
            "level": level,
        }
    )


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import PTARequest
from django.core.paginator import Paginator

@login_required
def pta_request_list(request):
    # Admin and teacher view all requests, parents view only theirs
    if request.user.role in ['ADMIN', 'STAFF']:
        requests = PTARequest.objects.all().order_by('-created_at')
    else:
        requests = PTARequest.objects.filter(parent=request.user).order_by('-created_at')

    # Pagination (10 per page)
    paginator = Paginator(requests, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'requests': page_obj
    }
    return render(request, 'pta/pta_request_list.html', context)
