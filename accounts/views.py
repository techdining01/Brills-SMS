from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, StudentCreateForm, TeacherCreateForm, ParentCreateForm
from .models import User
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from .models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt    
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_protect


User = get_user_model()

import logging
logger = logging.getLogger("system")


from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from .models import User


@csrf_protect
def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        role = request.POST.get("role")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if not all([username, email, role, password1, password2]):
            messages.error(request, "All fields are required.")
            return redirect("accounts:register")

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect("accounts:register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("accounts:register")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            role=role,
            is_active=True,
            is_approved=False,  
        )

        messages.success(
            request,
            "Registration successful. Await admin approval before login."
        )
        return redirect("accounts:login")

    return render(request, "accounts/register.html")


@csrf_protect
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, "Invalid username or password.")
            return redirect("accounts:login")

        if not user.is_approved:
            messages.warning(
                request,
                "Your account is pending approval. Contact admin."
            )
            return redirect("accounts:login")

        login(request, user)
        return redirect("accounts:dashboard_redirect")  # change if needed

    return render(request, "accounts/login.html")


@login_required
def logout_view(request):
    logout(request)
    return redirect("accounts:login")





@login_required
def complete_profile(request):
    user = request.user

    if request.method == "POST":
        user.phone_number = request.POST.get("phone_number")
        user.address = request.POST.get("address")
        user.emergency_contact = request.POST.get("emergency_contact")
        user.emergency_phone = request.POST.get("emergency_phone")

        if request.FILES.get("profile_picture"):
            user.profile_picture = request.FILES["profile_picture"]

        user.save()
        messages.success(request, "Profile completed successfully.")
        return redirect("accounts:dashboard_redirect")

    return render(request, "accounts/complete_profile.html")


def dashboard_redirect(request):
    user = request.user

    if not user.is_approved:
        return redirect('accounts:pending_approval')

    if user.role == "STUDENT":
        return redirect("exams:student_dashboard")
    elif user.role == "TEACHER":
        return redirect("exams:teacher_dashboard")
    elif user.role == "ADMIN":
        return redirect("exams:admin_dashboard")
    elif user.role == 'PARENT':
        return redirect('pickups:parent_dashboard')
   
    return redirect("accounts:login")




# @login_required
def post_login_router(request):
    user = request.user

    print("ROUTER:", user.username, user.role)

    if not user.is_approved:
        return redirect('accounts:pending_approval')

    if user.role == 'STUDENT':
        return redirect('exams:student_dashboard')

    if user.role == 'TEACHER':
        return redirect('exams:teacher_dashboard')

    if user.role == 'PARENT':
        return redirect('brillspay:parent_dashboard')

    if user.role == 'ADMIN':
        return redirect('/admin/')

    logout(request)
    return redirect('accounts:login')


@login_required
def create_student(request):
    if request.user.role != User.Role.ADMIN:
     return redirect('accounts:login')


    form = StudentCreateForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        student = form.save(commit=False)
        student.set_password(form.cleaned_data['password1'])
        student.save()
        messages.success(request, 'Student created successfully')
        if not student.is_approved:
            messages.warning(request, 'Account created. Awaiting admin approval.')
            return redirect('accounts:login')

        return redirect('accounts:create_student')

    return render(request, 'create_student.html', {'form': form})


@login_required
def pending_approval(request):
    return render(request, 'accounts/admin/pending_approval.html')


@staff_member_required
@login_required
def approve_users(request):
    role = request.GET.get('role')
    q = request.GET.get('q')

    users = User.objects.filter(is_approved=False)

    if role:
        users = users.filter(role=role)
        if q:
            users = users.filter(
            Q(username__icontains=q) |
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(email__icontains=q)
            )

    if request.method == 'POST':
        ids = request.POST.getlist('users')    
        # inside approve_users POST
        approved = User.objects.filter(id__in=ids)
        approved.update(is_approved=True)
        messages.success(request, f'{len(ids)} user(s) approved')

        for u in approved:
            send_mail(
            'Account Approved – Brills School',
            f'Hello {u.first_name}, Your account has been approved. You can now log in.',
            settings.DEFAULT_FROM_EMAIL,
            [u.email],
            fail_silently=True
            )
            return redirect('accounts:approve_users')

    return render(request, 'accounts/admin/approve_users.html', {
        'users': users,
        'roles': User.Role.choices
    })


@login_required
def admin_reset_password(request, user_id):
    if request.user.role != User.Role.ADMIN:
        return redirect('accounts:login')

    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        password = request.POST.get('password')
        user.set_password(password)
        user.save()

        send_mail(
        'Your Password Has Been Reset',
        f'Hello {user.first_name}, Your account password has been reset by the school admin. You can now log in normally.',
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=True
        )

        messages.success(request, f'Password reset for {user.username}')
        return redirect('accounts:approve_users')

    return render(request, 'accounts/admin/reset_password.html', {'u': user})


@staff_member_required
def admin_users(request):
    role = request.GET.get("role")
    status = request.GET.get("status")

    users = User.objects.all().order_by("-date_joined")

    if role:
        users = users.filter(role=role)

    if status == "pending":
        users = users.filter(is_approved=False)
    elif status == "approved":
        users = users.filter(is_approved=True)

    context = {
        "users": users,
        "role": role,
        "status": status,
    }
    return render(request, "accounts/admin/users/list.html", context)



@staff_member_required
def bulk_approve_users(request):
    if request.method == "POST":
        ids = request.POST.getlist("user_ids[]")

        updated = User.objects.filter(id__in=ids).update(is_approved=True)

        return JsonResponse({
            "success": True,
            "approved_count": updated
        })

    return JsonResponse({"success": False}, status=400)


