from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, StudentCreateForm, StaffCreateForm, ParentCreateForm
from .models import User
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings



def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')

    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        if not user.is_approved:
            messages.error(request, 'Account pending admin approval')
            return redirect('login')

        login(request, user)
        return redirect('dashboard_redirect')

    return render(request, 'auth/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard_redirect(request):
    role = request.user.role

    if role == User.Role.ADMIN:
        return redirect('admin_dashboard')
    elif role == User.Role.STAFF:
        return redirect('staff_dashboard')
    elif role == User.Role.STUDENT:
        return redirect('student_dashboard')
    elif role == User.Role.PARENT:
        return redirect('parent_dashboard')
    
    logout(request)
    return redirect('login')


@login_required
def create_student(request):
    if request.user.role != User.Role.ADMIN:
     return redirect('login')


    form = StudentCreateForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        student = form.save(commit=False)
        student.set_password(form.cleaned_data['password1'])
        student.save()
        messages.success(request, 'Student created successfully')
        if not student.is_approved:
            messages.warning(request, 'Account created. Awaiting admin approval.')
            return redirect('login')

        return redirect('create_student')

    return render(request, 'auth/create_student.html', {'form': form})


from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q


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
            return redirect('approve_users')

    return render(request, 'admin/approve_users.html', {
        'users': users,
        'roles': User.Role.choices
    })


@login_required
def admin_reset_password(request, user_id):
    if request.user.role != User.Role.ADMIN:
        return redirect('login')

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
        return redirect('approve_users')

    return render(request, 'admin/reset_password.html', {'u': user})


@login_required
def parent_dashboard(request):
    if request.user.role != User.Role.PARENT:
        return redirect('login')
    return render(request, 'parent/dashboard.html')


