from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q, Avg, Sum
from django.utils import timezone
from django.core.paginator import Paginator
from accounts.models import User
from exams.models import Exam, RetakeRequest, ChatMessage, SystemLog, Notification, Broadcast
from . import grading_views, exam_views, notification_views
from .forms import SchoolClassForm, StudentForm, ExamForm
from exams.models import Exam, RetakeRequest, ChatMessage, SystemLog, Notification, SchoolClass, Broadcast, ExamAttempt

# ========================= AUTHENTICATION =========================
def cbt_exam(request):
    return render(request, 'exams/cbt_home.html')

def about_page(request):
    return render(request, 'exams/about.html')
# ========================= DASHBOARDS =========================

@login_required()
def admin_dashboard(request):
    if request.user.role != User.Role.ADMIN:
        return redirect('accounts:dashboard_redirect')
    
    # Stats for admin
    total_students = User.objects.filter(role=User.Role.STUDENT).count()
    total_teachers = User.objects.filter(role=User.Role.TEACHER).count()
    total_exams = Exam.objects.all().count()
    total_classes = SchoolClass.objects.all().count()

    context = {


        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_exams': total_exams,
        'total_classes': total_classes
    }
    return render(request, 'dashboards/admin/dashboard.html', context)

@login_required()
def teacher_dashboard(request):
    if request.user.role != User.Role.TEACHER:
        return redirect('accounts:dashboard_redirect')
    return render(request, 'dashboards/teacher/dashboard.html')


@login_required()
def student_dashboard(request):
    if request.user.role != User.Role.STUDENT:
        return redirect('accounts:dashboard_redirect')
    
    student = request.user
    
    # Get available exams (active, published, for student's class)
    available_exams = Exam.objects.filter(
        school_class=student.student_class,
        is_published=True,
        is_active=True
    ).order_by('end_time')[:5]  # Show top 5 upcoming
    
    # Completed exams count
    completed_attempts = ExamAttempt.objects.filter(
        student=student, 
        status='submitted'
    )
    completed_exams = completed_attempts.count()
    
    # Average Score
    average_score = completed_attempts.aggregate(Avg('score'))['score__avg'] or 0
    
    # Simple Class Rank (based on average score of all students in class)
    class_students = User.objects.filter(role=User.Role.STUDENT, student_class=student.student_class)
    student_scores = []
    for s in class_students:
        s_avg = s.attempts.filter(status='submitted').aggregate(Avg('score'))['score__avg'] or 0
        student_scores.append(s_avg)
    
    student_scores.sort(reverse=True)
    try:
        class_rank = student_scores.index(average_score) + 1
    except ValueError:
        class_rank = "-"
        
    context = {
        'total_exams': Exam.objects.filter(school_class=student.student_class, is_published=True).count(),
        'available_exams': available_exams,
        'completed_exams': completed_exams,
        'average_score': round(average_score, 1),
        'class_rank': class_rank
    }
    
    return render(request, 'dashboards/student/dashboard.html', context)

@login_required()
def parent_dashboard(request):
    if request.user.role != User.Role.PARENT:
        return redirect('accounts:dashboard_redirect')
    children = request.user.children.all()
    return render(request, 'dashboards/parent/dashboard.html', {'children': children})

# ========================= ADMIN MANAGEMENT =========================

@login_required()
def admin_classes_list(request):
    classes = SchoolClass.objects.all()
    return render(request, 'dashboards/admin/classes_list.html', {'classes': classes})

@login_required()
def admin_create_class(request):
    if request.method == 'POST':
        form = SchoolClassForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Class created successfully.')
            return redirect('dashboards:admin_classes_list')
    else:
        form = SchoolClassForm()
    
    teachers = User.objects.filter(role=User.Role.TEACHER)
    levels = SchoolClass.LEVEL_CHOICES
    return render(request, 'dashboards/admin/create_class.html', {
        'form': form, 
        'teachers': teachers,
        'levels': levels
    })


@login_required()
def admin_edit_class(request, class_id):
    school_class = get_object_or_404(SchoolClass, id=class_id)
    if request.method == 'POST':
        form = SchoolClassForm(request.POST, instance=school_class)
        if form.is_valid():
            form.save()
            messages.success(request, 'Class updated successfully.')
            return redirect('dashboards:admin_classes_list')
    else:
        form = SchoolClassForm(instance=school_class)
    
    teachers = User.objects.filter(role=User.Role.TEACHER)
    levels = SchoolClass.LEVEL_CHOICES
    return render(request, 'dashboards/admin/edit_class.html', {
        'form': form, 
        'class': school_class, 
        'teachers': teachers,
        'levels': levels
    })

@login_required()
def admin_delete_class(request, class_id):
    school_class = get_object_or_404(SchoolClass, id=class_id)
    if request.method == 'POST':
        school_class.delete()
        messages.success(request, 'Class deleted successfully.')
        return redirect('dashboards:admin_classes_list')
    return render(request, 'dashboards/admin/class_confirm_delete.html', {'class': school_class})

@login_required()
def admin_exams_list(request):
    exams = Exam.objects.all()
    return render(request, 'dashboards/admin/exams_list.html', {'exams': exams})

@login_required()
def admin_students_list(request):
    # Search and Filter implementation
    query = request.GET.get('q')
    class_filter = request.GET.get('class')
    
    students = User.objects.filter(role=User.Role.STUDENT)
    
    if query:
        students = students.filter(
            Q(username__icontains=query) | 
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        )
    
    if class_filter:
        try:
            students = students.filter(student_class__id=class_filter)
        except:
            pass
        
    classes = SchoolClass.objects.all()
    
    context = {
        'students': students,
        'classes': classes,
        'selected_class': int(class_filter) if class_filter and class_filter.isdigit() else None,
        'search_query': query
    }
    return render(request, 'dashboards/admin/students_list.html', context)

@login_required()
def admin_create_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student created successfully.')
            return redirect('dashboards:admin_students_list')
    else:
        form = StudentForm()
    
    return render(request, 'dashboards/admin/create_student.html', {'form': form})

@login_required()
def admin_edit_student(request, student_id):
    student = get_object_or_404(User, id=student_id, role=User.Role.STUDENT)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student updated successfully.')
            return redirect('dashboards:admin_students_list')
    else:
        form = StudentForm(instance=student)
        
    return render(request, 'dashboards/admin/edit_student.html', {'form': form, 'student': student})

@login_required()
def admin_delete_student(request, student_id):
    student = get_object_or_404(User, id=student_id, role=User.Role.STUDENT)
    if request.method == 'POST':
        student.delete()
        messages.success(request, 'Student deleted successfully.')
        return redirect('dashboards:admin_students_list')
    return render(request, 'dashboards/admin/student_confirm_delete.html', {'student': student})

@login_required()
def broadcast_center(request):
    if request.user.role not in [User.Role.ADMIN, User.Role.TEACHER]:
        messages.error(request, 'Access denied')
        return redirect('dashboards:dashboard_redirect')
        
    if request.method == 'POST':
        title = request.POST.get('title')
        message_content = request.POST.get('message')
        target_class_id = request.POST.get('target_class')
        
        target_class = None
        if target_class_id:
            target_class = get_object_or_404(SchoolClass, id=target_class_id)
            
        broadcast = Broadcast.objects.create(
            sender=request.user,
            target_class=target_class,
            title=title,
            message=message_content
        )
        
        # Log broadcast creation
        SystemLog.objects.create(
            level='INFO',
            source='Broadcast',
            message=f"Broadcast '{title}' sent by {request.user.username} to {target_class.name if target_class else 'All Students'}"
        )
        
        # Create notifications for users
        recipients = User.objects.filter(role=User.Role.STUDENT)
        if target_class:
            recipients = recipients.filter(student_class=target_class)
            
        notifications = []
        for recipient in recipients:
            notifications.append(Notification(
                recipient=recipient,
                title=f"Broadcast: {title}",
                message=message_content,
                notification_type='general' # Assuming 'general' or 'broadcast' type exists or is allowed
            ))
        Notification.objects.bulk_create(notifications)
        
        messages.success(request, 'Broadcast sent successfully.')
        return redirect('dashboards:broadcast_center')
        
    broadcasts = Broadcast.objects.all().order_by('-created_at')
    classes = SchoolClass.objects.all()
    
    return render(request, 'dashboards/broadcast_center.html', {
        'broadcasts': broadcasts,
        'classes': classes
    })

@login_required()
def admin_retake_requests(request):
    status_filter = request.GET.get('status')
    
    requests_list = RetakeRequest.objects.all().order_by('-created_at')
    
    if status_filter:
        requests_list = requests_list.filter(status=status_filter)
        
    paginator = Paginator(requests_list, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    statuses = [('pending', 'Pending'), ('approved', 'Approved'), ('denied', 'Denied')]
    
    return render(request, 'dashboards/admin/retake_requests.html', {
        'page_obj': page_obj, 
        'statuses': statuses,
        'status_filter': status_filter
    })

@login_required()
def admin_system_logs(request):
    level_filter = request.GET.get('level')
    logs_list = SystemLog.objects.all().order_by('-created_at')
    
    if level_filter:
        logs_list = logs_list.filter(level=level_filter)
        
    paginator = Paginator(logs_list, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    levels = [c[0] for c in SystemLog.LEVEL_CHOICES]
    
    return render(request, 'dashboards/admin/system_logs.html', {
        'page_obj': page_obj,
        'levels': levels,
        'level_filter': level_filter
    })

@login_required()
def admin_leaderboard(request):
    class_id = request.GET.get('class')
    if class_id:
        school_class = get_object_or_404(SchoolClass, id=class_id)
        # Calculate leaderboard
        students = User.objects.filter(role=User.Role.STUDENT, student_class=school_class)
        leaderboard = []
        for student in students:
            attempts = student.attempts.filter(status='submitted')
            if attempts.exists():
                avg_score = attempts.aggregate(Avg('score'))['score__avg'] or 0
                total_score = attempts.aggregate(Sum('score'))['score__sum'] or 0
                leaderboard.append({
                    'student': student,
                    'class_name': school_class.name,
                    'total_score': total_score,
                    'exams_count': attempts.count(),
                    'average_score': avg_score
                })
        
        # Sort by average score
        leaderboard.sort(key=lambda x: x['average_score'], reverse=True)
        return render(request, 'dashboards/admin/leaderboard_detail.html', {'leaderboard': leaderboard, 'class': school_class})
    
    classes = SchoolClass.objects.all()
    return render(request, 'dashboards/admin/leaderboard.html', {'classes': classes})

# ========================= TEACHER ACTIONS =========================

@login_required()
def teacher_exams_list(request):
    exams = Exam.objects.filter(created_by=request.user)
    return render(request, 'dashboards/teacher/exams_list.html', {'exams': exams})

@login_required()
def teacher_subjective_grading(request):
    return grading_views.teacher_grading_dashboard(request)

@login_required()
def teacher_notifications(request):
    return notification_views.notifications_list(request)

# ========================= STUDENT ACTIONS =========================

@login_required()
def student_available_exams(request):
    student = request.user
    
    # Show published exams for student's class
    exams = Exam.objects.filter(
        school_class=student.student_class,
        is_published=True,
        is_active=True
    ).order_by('-created_at')
    
    # Search
    search_query = request.GET.get('search')
    if search_query:
        exams = exams.filter(title__icontains=search_query)

    # Pagination
    paginator = Paginator(exams, 12)  # Show 12 exams per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'dashboards/student/available_exams.html', {
        'page_obj': page_obj,
        'search_query': search_query
    })

@login_required()
def student_attempt_history(request):
    status_filter = request.GET.get('status')
    attempts = request.user.attempts.all().order_by('-started_at')
    
    if status_filter:
        attempts = attempts.filter(status=status_filter)
        
    paginator = Paginator(attempts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    statuses = ['in_progress', 'submitted', 'completed', 'interrupted', 'timed_out']
    
    return render(request, 'dashboards/student/attempt_history.html', {
        'page_obj': page_obj,
        'statuses': statuses,
        'status_filter': status_filter
    })

@login_required()
def student_class_leaderboard(request):
    user = request.user
    if user.role != User.Role.STUDENT:
        messages.error(request, 'Access denied')
        return redirect('accounts:dashboard_redirect')
        
    school_class = user.student_class
    if not school_class:
        messages.error(request, 'You are not assigned to any class.')
        return redirect('dashboards:student_dashboard')
        
    students = User.objects.filter(role=User.Role.STUDENT, student_class=school_class)
    
    leaderboard_data = []
    for student in students:
        attempts = student.attempts.filter(status='submitted')
        if attempts.exists():
            avg_score = attempts.aggregate(Avg('score'))['score__avg'] or 0
            leaderboard_data.append({
                'student': student,
                'avg_score': avg_score,
                'attempt_count': attempts.count(),
                'is_self': student == user
            })
    
    # Sort
    leaderboard_data.sort(key=lambda x: x['avg_score'], reverse=True)
    
    # Add rank
    for i, entry in enumerate(leaderboard_data):
        entry['rank'] = i + 1
        
    # Pagination
    paginator = Paginator(leaderboard_data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'dashboards/student/class_leaderboard.html', {
        'school_class': school_class, 
        'page_obj': page_obj
    })

@login_required()
def student_notifications(request):
    return notification_views.notifications_list(request)

@login_required()
def student_request_retake(request):
    if request.user.role != User.Role.STUDENT:
        messages.error(request, 'Access denied')
        return redirect('login')
    
    if request.method == 'POST':
        exam_id = request.POST.get('exam_id')
        reason = request.POST.get('reason')
        exam = get_object_or_404(Exam, id=exam_id)
        
        if RetakeRequest.objects.filter(student=request.user, exam=exam, status='pending').exists():
            messages.error(request, 'You already have a pending retake request for this exam.')
        else:
            RetakeRequest.objects.create(student=request.user, exam=exam, reason=reason)
            messages.success(request, 'Retake request submitted.')
            
    return redirect('dashboards:student_dashboard')

# ========================= PARENT ACTIONS =========================

@login_required()
def parent_children_list(request):
    children = request.user.children.all()
    return render(request, 'dashboards/parent/children_list.html', {'children': children})

@login_required()
def parent_child_results(request, child_id):
    child = get_object_or_404(User, id=child_id)
    # Ensure this child belongs to the logged-in parent
    if not request.user.children.filter(id=child_id).exists():
        messages.error(request, 'Access denied')
        return redirect('dashboards:parent_dashboard')
        
    attempts = child.attempts.filter(status='submitted').order_by('-started_at')
    return render(request, 'dashboards/parent/child_results.html', {'child': child, 'attempts': attempts})

@login_required()
def parent_notifications(request):
    return notification_views.notifications_list(request)

# ========================= EXAM ACTIONS =========================

@login_required()
def exam_detail(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    return render(request, 'exams/exam_detail.html', {'exam': exam})

@login_required()
def create_exam(request):
    if request.method == 'POST':
        # Check for JSON request (AJAX)
        if request.content_type == 'application/json':
            import json
            from django.db import transaction
            from django.http import JsonResponse
            from django.urls import reverse
            from exams.models import Question, Choice

            try:
                data = json.loads(request.body)
                exam_data = data.get('exam', {})
                questions_data = data.get('questions', [])
                
                form = ExamForm(exam_data)
                
                if form.is_valid():
                    with transaction.atomic():
                        exam = form.save(commit=False)
                        exam.created_by = request.user
                        exam.save()
                        
                        # Save Questions
                        for index, q_data in enumerate(questions_data):
                            question = Question.objects.create(
                                exam=exam,
                                text=q_data.get('text'),
                                type=q_data.get('type'),
                                marks=int(q_data.get('marks', 1)),
                                order=index + 1
                            )
                            
                            if question.type == 'objective':
                                choices = q_data.get('choices', [])
                                for c_data in choices:
                                    Choice.objects.create(
                                        question=question,
                                        text=c_data.get('text'),
                                        is_correct=c_data.get('is_correct', False)
                                    )
                                    
                    redirect_url = reverse('dashboards:teacher_exams_list')
                    if request.user.role == User.Role.ADMIN:
                        redirect_url = reverse('dashboards:admin_exams_list')
                        
                    messages.success(request, 'Exam and questions created successfully.')
                    return JsonResponse({'status': 'success', 'redirect_url': redirect_url})
                else:
                    return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
            
            except Exception as e:
                import traceback
                print(traceback.format_exc())
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

        form = ExamForm(request.POST)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.created_by = request.user
            exam.save()
            messages.success(request, 'Exam created successfully.')
            if request.user.role == User.Role.ADMIN:
                return redirect('dashboards:admin_exams_list')
            else:
                return redirect('dashboards:teacher_exams_list')
    else:
        form = ExamForm()
    classes = SchoolClass.objects.all()
    
    return render(request, 'exams/create_exam.html', {'form': form, 'classes': classes})

@login_required()
def edit_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    if request.user != exam.created_by and request.user.role != User.Role.ADMIN:
        messages.error(request, 'Access denied')
        return redirect('dashboards:accounts:dashboard_redirect')
        
    if request.method == 'POST':
        form = ExamForm(request.POST, instance=exam)
        if form.is_valid():
            form.save()
            messages.success(request, 'Exam updated successfully.')
            if request.user.role == User.Role.ADMIN:
                return redirect('dashboards:admin_exams_list')
            else:
                return redirect('dashboards:teacher_exams_list')
    else:
        form = ExamForm(instance=exam)
    
    return render(request, 'exams/edit_exam.html', {'form': form, 'exam': exam})

@login_required()
def delete_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    if request.user != exam.created_by and request.user.role != User.Role.ADMIN:
        messages.error(request, 'Access denied')
        return redirect('accounts:dashboard')
        
    if request.method == 'POST':
        exam.delete()
        messages.success(request, 'Exam deleted successfully.')
        if request.user.role == User.Role.ADMIN:
            return redirect('dashboards:admin_exams_list')
        else:
            return redirect('dashboards:teacher_exams_list')
            
    return render(request, 'exams/exam_confirm_delete.html', {'exam': exam})

@login_required()
def publish_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    if request.user != exam.created_by and request.user.role != User.Role.ADMIN:
        messages.error(request, 'Access denied')
        return redirect('dashboards:exam_detail', exam_id=exam.id)
    exam.is_published = True
    exam.save()
    messages.success(request, 'Exam published successfully.')
    return redirect('dashboards:exam_detail', exam_id=exam.id)

@login_required()
def unpublish_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    if request.user != exam.created_by and request.user.role != User.Role.ADMIN:
        messages.error(request, 'Access denied')
        return redirect('dashboards:exam_detail', exam_id=exam.id)
    exam.is_published = False
    exam.save()
    messages.warning(request, 'Exam unpublished.')
    return redirect('dashboards:exam_detail', exam_id=exam.id)

# ========================= CHAT SYSTEM =========================

@login_required()
def chat_list(request):
    """List of conversations"""
    user = request.user
    
    # Restrict to Admin and Teacher only
    if user.role not in [User.Role.ADMIN, User.Role.TEACHER]:
        messages.error(request, 'Access denied. Chat is available for staff only.')
        return redirect('accounts:dashboard_redirect')
    
    # Get users who have exchanged messages
    sent_to = ChatMessage.objects.filter(sender=user).values_list('recipient', flat=True)
    received_from = ChatMessage.objects.filter(recipient=user).values_list('sender', flat=True)
    
    user_ids = set(list(sent_to) + list(received_from))
    
    # Also include admins if user is teacher, or teachers if user is admin
    if user.role == User.Role.TEACHER:
        admins = User.objects.filter(role=User.Role.ADMIN).values_list('id', flat=True)
        user_ids.update(admins)
    elif user.role == User.Role.ADMIN:
        teachers = User.objects.filter(role=User.Role.TEACHER).values_list('id', flat=True)
        user_ids.update(teachers)
        
    # Filter out students from the conversation list just in case
    conversations = User.objects.filter(id__in=user_ids).exclude(id=user.id).exclude(role=User.Role.STUDENT)
    
    # Annotate with last message
    conversation_list = []
    for partner in conversations:
        last_msg = ChatMessage.objects.filter(
            Q(sender=user, recipient=partner) | Q(sender=partner, recipient=user)
        ).order_by('-created_at').first()
        
        unread_count = ChatMessage.objects.filter(
            sender=partner, recipient=user, is_read=False
        ).count()
        
        conversation_list.append({
            'user': partner,
            'last_message': last_msg,
            'unread_count': unread_count
        })
    
    # Sort by last message time
    conversation_list.sort(key=lambda x: x['last_message'].created_at if x['last_message'] else timezone.now(), reverse=True)
    
    return render(request, 'dashboards/chat/chat_list.html', {'conversations': conversation_list})

@login_required()
def chat_detail(request, user_id):
    """Chat conversation with a specific user"""
    user = request.user

    # Restrict to Admin and Teacher only
    if user.role not in [User.Role.ADMIN, User.Role.TEACHER]:
        messages.error(request, 'Access denied.')
        return redirect('accounts:dashboard_redirect')

    other_user = get_object_or_404(User, id=user_id)
    
    # Prevent chatting with students or self
    if other_user.role == User.Role.STUDENT or other_user == user:
        messages.error(request, 'Invalid chat partner.')
        return redirect('dashboards:chat_list')
    
    # Mark messages as read
    ChatMessage.objects.filter(sender=other_user, recipient=user, is_read=False).update(is_read=True)
    
    messages_list = ChatMessage.objects.filter(
        Q(sender=user, recipient=other_user) | Q(sender=other_user, recipient=user)
    ).order_by('created_at')
    
    if request.method == 'POST':
        content = request.POST.get('message')
        if content:
            ChatMessage.objects.create(
                sender=user,
                recipient=other_user,
                message=content
            )
            
            # Log chat message
            SystemLog.objects.create(
                level='INFO',
                source='Chat',
                message=f"Message sent from {user.username} ({user.get_role_display()}) to {other_user.username} ({other_user.get_role_display()})"
            )
            
            return redirect('dashboards:chat_detail', user_id=user_id)
            
    return render(request, 'dashboards/chat/chat_detail.html', {
        'other_user': other_user,
        'messages': messages_list
    })

# ========================= NOTIFICATIONS =========================

@login_required()
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save()
    return redirect(request.META.get('HTTP_REFERER', 'accounts_redirect'))

@login_required()
def mark_all_notifications_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    messages.success(request, 'All notifications marked as read.')
    return redirect(request.META.get('HTTP_REFERER', 'accounts_redirect'))
