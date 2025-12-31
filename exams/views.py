import re
from django.urls import reverse
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
from accounts.models import User
from django.db.models import Sum, Avg, F    
from brillspay.models import Transaction
from pickup.models import PickupAuthorization
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db.models import Sum, Count
from brillspay.models import Order
from exams.models import Exam, ExamAttempt
from django.utils.timezone import now
from datetime import timedelta
from django.shortcuts import redirect
from django.contrib import messages
from .utils import has_paid_for_exam
from exams.models import Exam, Broadcast, PTARequest
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.shortcuts import render
from .models import SystemLog
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import PTARequest
from django.core.paginator import Paginator

from django.db.models import Count, Sum
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Exam, ExamAttempt, StudentAnswer, SubjectiveMark, ExamAccess
from django.db.models import Sum
import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from .models import Exam, ExamAttempt, ExamAccess
from django.db.models import Sum
from django.http import HttpResponseForbidden




from brillspay.models import PaymentTransaction, Order
from exams.models import Exam, ExamAttempt
from accounts.models import User
from exams.models import ExamAccess
import random
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Exam, ExamAttempt, Question, StudentAnswer, Choice, ExamAccess, SubjectiveMark
from django.views.decorators.http import require_POST
from reportlab.lib.colors import lightgrey
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.http import HttpResponse
import os
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing



import logging
logger = logging.getLogger("system")

def teacher_required(user):
    return user.is_authenticated and user.role == 'TEACHER'


def cbt_exam(request):
    return render(request, 'exams/home.html')

@login_required
@user_passes_test(teacher_required)
def create_exam(request):
    classes = SchoolClass.objects.all()
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
        return redirect('exams:teacher_exam_list')

    return render(request, 'exams/teacher/create_exam.html', { 'classes': classes})

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
        return redirect('exams:question_list', exam_id=exam.id)

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
    return render(request, 'exams/admin/exams/list.html', {'exams': exams})


@login_required
@user_passes_test(admin_required)
def toggle_exam_publish(request, pk):
    exam = Exam.objects.get(pk=pk)
    exam.is_published = not exam.is_published
    exam.save(update_fields=['is_published'])
    return redirect('exams:admin_exam_list')



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
            return redirect('exams:question_list', exam.id)

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
        return redirect('exams:question_list', exam.id)

    return render(request, 'exams/teacher/upload_excel.html', {'exam': exam})


@login_required
@user_passes_test(teacher_required)
def upload_questions_word(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)

    if request.method == 'POST':
        file = request.FILES.get('file')
        if not file or not file.name.endswith('.docx'):
            messages.error(request, "Please upload a valid .docx file.")
            return redirect('exams:question_list', exam.id)

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

        return redirect('exams:question_list', exam.id)

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

#### ======= Student Exam Views ======= ####

@login_required
def student_dashboard(request):
    student = request.user

    # AVAILABLE EXAMS
    accessible_exam_ids = ExamAccess.objects.filter(
        student=student
    ).values_list('exam_id', flat=True)

    active_attempts = ExamAttempt.objects.filter(
        student=student,
        status='in_progress'
    )

    attempted_exam_ids = ExamAttempt.objects.filter(
        student=student,
        status='submitted'
    ).values_list('exam_id', flat=True)

    available_exams = Exam.objects.filter(
        id__in=accessible_exam_ids,
        is_published=True
    ).exclude(id__in=attempted_exam_ids)

    past_attempts = ExamAttempt.objects.filter(
        student=student,
        status='submitted'
    ).select_related('exam')

    # PERFORMANCE CHART
    chart_data = {
        "labels": [a.exam.title for a in past_attempts],
        "scores": [a.total_score for a in past_attempts]
    }

    # LEADERBOARD (NO subjective_mark join!)
    leaderboard = (
        ExamAttempt.objects
        .filter(
            exam__school_class=student.student_class,
            status='submitted'
        )
        .values(
            'student__first_name',
            'student__last_name'
        )
        .annotate(total=Sum('score'))
        .order_by('-total')[:10]
    )

    return render(request, "exams/student_dashboard.html", {
        "available_exams": available_exams,
        "active_attempts": active_attempts,
        "past_attempts": past_attempts,
        "chart": chart_data,
        "leaderboard": leaderboard
    })


@login_required
def parent_dashboard(request):
    parent = request.user
    wards = parent.children.all()

    attempts = ExamAttempt.objects.filter(
        student__in=wards,
        status='submitted'
    )

    return render(request, "exams/parent/dashboard.html", {
        "wards": wards,
        "attempts": attempts
    })


@staff_member_required
def admin_exam_analytics(request):
    stats = ExamAttempt.objects.filter(
        status='submitted'
    ).values('exam__title').annotate(
        avg=Avg('score'),
        count=Count('id')
    )

    return render(request, "exams/admin/analytics.html", {"stats": stats})



@login_required
def start_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    questions = Question.objects.filter(exam=exam).prefetch_related('choices')
    question_ids = list(
        Question.objects
        .filter(exam=exam)
        .values_list("id", flat=True)
    )

    random.shuffle(question_ids)

    attempt = ExamAttempt.objects.create(
        student=request.user,
        exam=exam,
        question_order=question_ids,   # ✅ LIST, NOT STRING
        remaining_seconds=exam.duration * 60,
        status="in_progress"
    )

    # map answers by question_id
    answers = {
        ans.question_id: ans
        for ans in StudentAnswer.objects.filter(attempt=attempt)
    }

    # 🔥 attach answer info directly to question
    # for q in questions:
    #     ans = answers.get(q.id)

    #     q.selected_choice_id = ans.selected_choice_id if ans else None
    #     q.text_answer = ans.answer_text if ans else ""
    #     q.selected_choices = (
    #         list(ans.selected_choices.values_list("id", flat=True))
    #         if ans and hasattr(ans, "selected_choices")
    #         else []
    #     )

    return render(request, "exams/start_exam.html", {
        "exam": exam,
        "attempt": attempt,
        "questions": questions,
    })



@login_required
def submit_exam(request, attempt_id):
    attempt = get_object_or_404(
        ExamAttempt,
        id=attempt_id,
        student=request.user
    )

    score = 0
    for answer in attempt.answers.select_related("question", "selected_choice"):
        if answer.question.type == "objective":
            if answer.selected_choice and answer.selected_choice.is_correct:
                score += answer.question.marks

    attempt.score = score
    attempt.status = "submitted"
    attempt.is_submitted = True
    attempt.completed_at = timezone.now()
    attempt.save()

    return redirect("exams:review_exam", attempt_id=attempt.id)


@login_required
def review_exam(request, attempt_id):
    attempt = get_object_or_404(
        ExamAttempt,
        id=attempt_id,
        student=request.user
    )

    return render(request, "exams/student/review.html", {
        "attempt": attempt,
        "answers": attempt.answers.select_related(
            "question", "selected_choice", "subjective_mark"
        )
    })

@login_required
def toggle_exam_access(request, student_id, exam_id):
    access, created = ExamAccess.objects.get_or_create(
        student_id=student_id,
        exam_id=exam_id
    )
    access.delete() if not created else None
    return redirect("admin_exam_access")


@login_required
def exam_chart(request, attempt_id):
    attempt = get_object_or_404(
        ExamAttempt,
        id=attempt_id,
        student=request.user
    )

    return render(request, "exams/student/chart.html", {
        "objective": attempt.score,
        "subjective": attempt.subjective_score,
    })


from reportlab.lib.colors import red, green

def draw_status_stamp(canvas, status):
    canvas.saveState()
    canvas.setFont("Helvetica-Bold", 36)

    if status == "APPROVED":
        canvas.setStrokeColor(green)
        canvas.setFillColor(green)
    else:
        canvas.setStrokeColor(red)
        canvas.setFillColor(red)

    canvas.translate(350, 200)
    canvas.rotate(20)
    canvas.drawCentredString(0, 0, status)
    canvas.restoreState()


def draw_watermark(canvas, text):
    canvas.saveState()
    canvas.setFont("Helvetica-Bold", 60)
    canvas.setFillColor(lightgrey)
    canvas.translate(300, 400)
    canvas.rotate(45)
    canvas.drawCentredString(0, 0, text)
    canvas.restoreState()


def draw_qr(canvas, url, x=50, y=120):
    qr_code = qr.QrCodeWidget(url)
    bounds = qr_code.getBounds()
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]

    d = Drawing(100, 100, transform=[100./width,0,0,100./height,0,0])
    d.add(qr_code)
    d.drawOn(canvas, x, y)


@login_required
def export_result_pdf(request, attempt_id):
    attempt = get_object_or_404(
        ExamAttempt,
        id=attempt_id,
        student=request.user
    )
    
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="exam_result_{attempt.id}.pdf"'
    )

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # 🔷 HEADER
    if os.path.exists(settings.SCHOOL_LOGO):
        p.drawImage(
            settings.SCHOOL_LOGO,
            40, height - 120,
            width=80, height=80,
            preserveAspectRatio=True
        )

    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width / 2, height - 60, settings.SCHOOL_NAME)

    p.setFont("Helvetica", 10)
    p.drawCentredString(width / 2, height - 80, settings.SCHOOL_ADDRESS)

    # Student photo
    if attempt.student.profile_picture:
        p.drawImage(
            attempt.student.profile_picture.path,
            width - 120, height - 120,
            width=80, height=80,
            preserveAspectRatio=True
        )

    status = "APPROVED" if attempt.is_fully_graded else "PENDING"
    draw_status_stamp(p, status)

    draw_watermark(p, settings.SCHOOL_NAME)

    y = height - 150
    p.setFont("Helvetica", 12)

    p.drawString(50, y, f"Student: {attempt.student.get_full_name()}")
    y -= 20
    p.drawString(50, y, f"Exam: {attempt.exam.title}")
    y -= 20
    p.drawString(50, y, f"Total Score: {attempt.total_score}")

    # Question review
    y -= 30
    for answer in attempt.answers.select_related(
        "question", "selected_choice"
    ).prefetch_related("question__choices"):

        if y < 100:
            p.showPage()
            draw_watermark(p, settings.SCHOOL_NAME)
            y = height - 100

        q = answer.question
        p.drawString(50, y, f"Q: {q.text}")
        y -= 15

        if q.type == "objective":
            correct = q.choices.filter(is_correct=True).first()
            p.drawString(
                70, y,
                f"Your Answer: {answer.selected_choice.text if answer.selected_choice else 'None'}"
            )
            y -= 15
            p.drawString(70, y, f"Correct: {correct.text if correct else 'N/A'}")
            y -= 20
        else:
            p.drawString(70, y, f"Answer: {answer.answer_text}")
            y -= 15
            p.drawString(
                70, y,
                f"Score: {answer.subjective_mark.score if hasattr(answer,'subjective_mark') else 'Pending'}"
            )
            y -= 20
            
    verify_url = request.build_absolute_uri(
        reverse("verify_result", args=[
        attempt.id,
        attempt.verification_token
        ])
    )
    
    draw_qr(p, verify_url)
    p.save()
    return response



@staff_member_required
def admin_bulk_exam_results_pdf(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)

    attempts = (
        ExamAttempt.objects
        .filter(exam=exam, status="submitted")
        .select_related("student")
        .order_by("-score")
    )

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="{exam.title}_results.pdf"'
    )

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    y = height - 100

    for attempt in attempts:
        status = "APPROVED" if attempt.is_fully_graded else "PENDING"

    draw_status_stamp(p, status)

    draw_watermark(p, settings.SCHOOL_NAME)

    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width / 2, height - 60, f"{exam.title} Results")

    y -= 40
    p.setFont("Helvetica-Bold", 11)
    p.drawString(50, y, "Student")
    p.drawString(300, y, "Total Score")
    y -= 20

    p.setFont("Helvetica", 11)

    for attempt in attempts:

        if y < 80:
            p.showPage()
            draw_watermark(p, settings.SCHOOL_NAME)
            draw_status_stamp(p, status)  # for all students
            y = height - 80

        p.drawString(50, y, attempt.student.get_full_name())
        p.drawString(300, y, str(attempt.total_score))
        y -= 18

    verify_url = request.build_absolute_uri(
        reverse("exams:verify_result", args=[
        attempt.id,
        attempt.verification_token
        ])
    )
    draw_qr(p, verify_url)
    p.save()
    return response



@login_required
def teacher_grading_summary_pdf(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)

    if request.user != exam.created_by and not request.user.is_superuser:
        return HttpResponse("Unauthorized", status=403)

    answers = (
        StudentAnswer.objects
        .filter(
            question__exam=exam,
            question__type="subjective"
        )
        .select_related("attempt__student", "subjective_mark")
    )

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="{exam.title}_grading_summary.pdf"'
    )

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    y = height - 80

    status = "APPROVED" if StudentAnswer.attempt.is_fully_graded else "PENDING"
    draw_status_stamp(p, status)
    draw_watermark(p, settings.SCHOOL_NAME)

    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width / 2, height - 50, "Subjective Grading Summary")

    y -= 40
    p.setFont("Helvetica", 11)

    for ans in answers:
        if y < 100:
            p.showPage()
            draw_watermark(p, settings.SCHOOL_NAME)
            draw_status_stamp(p, status)  # for all students
            y = height - 80

        p.drawString(50, y, f"Student: {ans.attempt.student.get_full_name()}")
        y -= 15
        p.drawString(50, y, f"Question: {ans.question.text}")
        y -= 15
        p.drawString(50, y, f"Answer: {ans.answer_text}")
        y -= 15
        p.drawString(
            50, y,
            f"Score: {ans.subjective_mark.score if hasattr(ans,'subjective_mark') else 'Pending'}"
        )
        y -= 30

    verify_url = request.build_absolute_uri(
        reverse("verify_result", args=[
        StudentAnswer.attempt.id,
        StudentAnswer.attempt.verification_token
        ])
    )
    draw_qr(p, verify_url)
    p.save()
    return response



@login_required
@require_POST
def autosave_answer(request):
    attempt_id = request.POST.get("attempt_id")
    question_id = request.POST.get("question_id")
    choice_id = request.POST.get("choice_id")
    text = request.POST.get("text")
    remaining_seconds = request.POST.get("remaining_seconds")

    attempt = get_object_or_404(
        ExamAttempt,
        id=attempt_id,
        student=request.user,
        status="in_progress"
    )

    question = get_object_or_404(Question, id=question_id)

    answer, _ = StudentAnswer.objects.get_or_create(
        attempt=attempt,
        question=question
    )

    if question.type == "objective":
        answer.selected_choice_id = choice_id
    else:
        answer.answer_text = text

    answer.save()

    attempt.remaining_seconds = remaining_seconds
    attempt.save(update_fields=["remaining_seconds", "last_activity_at"])

    return JsonResponse({"saved": True})


@login_required
def grade_subjective(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)

    if request.user != exam.created_by and not request.user.is_superuser:
        return HttpResponseForbidden()

    answers = StudentAnswer.objects.filter(
        question__exam=exam,
        question__type="subjective"
    ).select_related("attempt", "question")

    return render(request, "exams/teacher/grade_subjective.html", {
        "answers": answers,
        "exam": exam
    })



# ----------------------------
# Admin: Grant/Revoke Exam Access
# ----------------------------
# @staff_member_required
# def admin_exam_access(request):
#     exams = Exam.objects.all().order_by("-created_at")
#     students = User.objects.filter(role="STUDENT").order_by("first_name")
    
#     if request.method == "POST":
#         exam_id = request.POST.get("exam_id")
#         student_id = request.POST.get("student_id")
#         action = request.POST.get("action")  # grant or revoke
#         exam = get_object_or_404(Exam, id=exam_id)
#         student = get_object_or_404(User, id=student_id, role="STUDENT")

#         if action == "grant":
#             ExamAccess.objects.get_or_create(student=student, exam=exam)
#             messages.success(request, f"Access granted to {student.get_full_name()} for {exam.title}")
#         elif action == "revoke":
#             ExamAccess.objects.filter(student=student, exam=exam).delete()
#             messages.success(request, f"Access revoked from {student.get_full_name()} for {exam.title}")
#         return redirect("exams:admin_exam_access")

#     # Build dict of student -> exams granted
#     access_dict = {}
#     for student in students:
#         granted_exams = ExamAccess.objects.filter(student=student).values_list('exam_id', flat=True)
#         access_dict[student.id] = list(granted_exams)

#     context = {
#         "exams": exams,
#         "students": students,
#         "access_dict": access_dict,
#     }
#     return render(request, "exams/admin/exams/exam_access_list.html", context)

# ----------------------------
# Admin: View Student Attempts for an Exam
# ----------------------------
@staff_member_required
def admin_exam_attempts(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    attempts = ExamAttempt.objects.filter(exam=exam, status='submitted') \
        .select_related('student') \
        .annotate(total_score=Sum('score') + Sum('subjective_score'))
    
    context = {
        "exam": exam,
        "attempts": attempts,
    }
    return render(request, "exams/admin_exam_attempts.html", context)

# ----------------------------
# Admin: Reset Attempt (for Retake)
# ----------------------------
@staff_member_required
def admin_reset_attempt(request, attempt_id):
    attempt = get_object_or_404(ExamAttempt, id=attempt_id)
    # Archive current attempt
    attempt.status = "archived"
    attempt.save()

    # Create new ExamAttempt with same exam/student, new random question order
    import random
    questions = list(attempt.exam.question_set.values_list('id', flat=True))
    random.shuffle(questions)

    ExamAttempt.objects.create(
        student=attempt.student,
        exam=attempt.exam,
        question_order=questions,
        status='in_progress',
        remaining_seconds=attempt.exam.duration * 60,
        retake_allowed=True,
    )

    messages.success(request, f"Attempt for {attempt.student.get_full_name()} has been reset.")
    return redirect("exams:admin_exam_attempts", exam_id=attempt.exam.id)


@login_required
def student_leaderboard(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    attempts = ExamAttempt.objects.filter(
        exam=exam, status="submitted"
    ).select_related('student')

    # Sort by total score
    attempts = sorted(attempts, key=lambda x: x.total_score, reverse=True)

    context = {
        "exam": exam,
        "attempts": attempts,
    }
    return render(request, "exams/student_leaderboard.html", context)


def verify_result(request, attempt_id, token):
    attempt = get_object_or_404(
        ExamAttempt,
        id=attempt_id,
        verification_token=token
    )

    return render(request, "exams/verify_result.html", {
        "attempt": attempt
    })


###======================END STUDENT EXAM VIEWS======================###



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
        return redirect('exams:exam_list')

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
            return redirect('exams:exam_list')

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
        return redirect('exams:exam_list')

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
        return redirect('exams:manage_retake')

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
        return redirect('exams:send_broadcast')

    return render(request, 'exams/notifications/broadcast.html')


##############################################################################

# @login_required
# def take_exam(request, exam_id):
#     exam = get_object_or_404(Exam, id=exam_id)
#     user = request.user
#     exam = get_object_or_404(Exam, id=exam_id, is_published=True)

#     if exam.requires_payment:
#         if not has_paid_for_exam(request.user, exam):
#             messages.warning(request, "Payment required to access this exam")
#             return redirect("exams:brillspay:exam_checkout", exam.id)



#     # Check active window
#     now = timezone.now()
#     if now < exam.start_time or now > exam.end_time:
#         messages.warning(request, "Exam is not active.")
#         return redirect('exams:student_dashboard')

#     # Get existing attempt or create new
#     attempt, created = ExamAttempt.objects.get_or_create(
#         exam=exam, student=user,
#         defaults={'remaining_seconds': exam.duration * 60}
#     )

#     # Resume remaining time
#     if request.method == 'POST':
#         # Save answers asynchronously via JS (fetch)
#         pass  # we'll handle AJAX later

#     questions = list(exam.question_set.all())
#     return render(request, 'exams/student/take_exam.html', {
#         'exam': exam,
#         'attempt': attempt,
#         'questions': questions
#     })



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
        return redirect('exams:student_dashboard')

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
        return redirect('exams:student_dashboard')

    # Fallback: redirect if not POST
    return redirect('exams:take_exam', exam_id=exam.id)



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
    return redirect('exams:retake_requests_list')


@login_required
def teacher_grading_dashboard(request):
    user = request.user
    if user.role != 'STAFF':
        messages.error(request, "Access denied.")
        return redirect('exams:home')

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


@staff_member_required
def admin_analytics_dashboard(request):
    # Revenue (last 30 days)
    last_30 = now() - timedelta(days=30)

    revenue_qs = (
        Order.objects.filter(status='STATUS.PAID', created_at__gte=last_30)
        .values("created_at__date")
        .annotate(total=Sum("total_amount"))
        .order_by("created_at__date")
    )

    revenue_labels = [str(r["created_at__date"]) for r in revenue_qs]
    revenue_data = [float(r["total_amount"]) for r in revenue_qs]

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
    return render(request, "exams/admin/analytics/dashboard.html", context)


@staff_member_required
def grant_exam_access(request):
    if request.method == "POST":
        ExamAccess.objects.create(
            student_id=request.POST["student"],
            exam_id=request.POST["exam"],
            reason=request.POST.get("reason", ""),
            granted_by=request.user
        )
        messages.success(request, "Exam access granted")
        return redirect("exams:grant_exam_access")

    context = {
        "students": User.objects.filter(role="STUDENT"),
        "exams": Exam.objects.all()
    }
    return render(request, "exams/admin/exams/grant_access.html", context)


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
        "exams/teachers/analytics/dashboard.html",
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

    return render(request, "exams/admin/analytics/communication.html", {
        "pta_stats": pta_stats,
        "broadcasts": broadcasts
    })



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
        "exams/admin/system_logs/logs.html",
        {
            "logs": page_obj,
            "level": level,
        }
    )


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
    return render(request, 'exams/pta/pta_request_list.html', context)



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

    return render(request, 'exams/parent/dashboard.html', {
        'children': children,
        'pta_requests': pta_requests,
        'notifications': notifications,
    })




@login_required
def teacher_dashboard(request):
    user = request.user

    if user.role != 'STAFF':
        return redirect('accounts:login')

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

    return render(request, 'exams/teacher/dashboard.html', {
        'exams': exams,
        'pending_marking': pending_marking,
        'notifications': notifications,
    })




def is_admin(user):
    return user.is_authenticated and user.role == "ADMIN"


@login_required
@user_passes_test(lambda u: u.role == "ADMIN")
def admin_dashboard(request):
    from exams.models import Exam, ExamAttempt, Notification

    context = {
        "total_exams": Exam.objects.count(),
        "published_exams": Exam.objects.filter(is_published=True).count(),
        "total_attempts": ExamAttempt.objects.count(),
        "pending_retake_requests": ExamAttempt.objects.filter(
            retake_allowed=False, status="submitted"
        ).count(),
        "unread_notifications": Notification.objects.filter(
            recipient=request.user, is_read=False
        ).count(),
    }
    return render(request, "exams/admin/dashboard.html", context)



def is_admin(user):
    return user.is_authenticated and user.role == User.Role.ADMIN



# @login_required(login_url="accounts:login")
# @user_passes_test(is_admin)
# def admin_analytics_chart(request):
#     today = timezone.now().date()
#     last_30 = today - timedelta(days=30)

#     revenue = (
#         PaymentTransaction.objects
#         .filter(status="success", created_at__date__gte=last_30)
#         .extra(select={'day': "date(created_at)"})
#         .values('day')
#         .annotate(total=Sum('amount'))
#         .order_by('day')
#     )

#     orders = Order.objects.values('status').annotate(count=Count('id'))

#     exam_stats = Exam.objects.annotate(
#         attempts=Count('examattempt')
#     ).values('title', 'attempts')

#     user_roles = User.objects.values('role').annotate(count=Count('id'))

#     return JsonResponse({
#         "revenue": list(revenue),
#         "orders": list(orders),
#         "exams": list(exam_stats),
#         "users": list(user_roles),
#     })

