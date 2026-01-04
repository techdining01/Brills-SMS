from django.contrib import admin
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from exams.models import Exam, ExamAttempt, PTARequest
from django.utils import timezone
from brillspay.models import Transaction, Order
from pickup.models import PickupAuthorization
from django.db.models import Sum





User = get_user_model()

def is_admin(user):
    return user.is_authenticated and user.role == User.Role.ADMIN


def landing_page(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard_redirect')
    return render(request, 'exams/landing.html')


def about_page(request):
    return render(request, 'exams/about.html')

@login_required(login_url='accounts:login')
@user_passes_test(is_admin)
def admin_mega_dashboard(request):
    # ==========================
    # USERS
    # ==========================
    total_users = User.objects.count()
    pending_users = User.objects.filter(is_approved=False).count()
    students = User.objects.filter(role=User.Role.STUDENT).count()
    parents = User.objects.filter(role=User.Role.PARENT).count()
    staff = User.objects.filter(role=User.Role.TEACHER).count()

    # ==========================
    # EXAMS
    # ==========================
    total_exams = Exam.objects.count()
    active_exams = Exam.objects.filter(
        is_active=True,
        start_time__lte=timezone.now(),
        end_time__gte=timezone.now()
    ).count()
    attempts_today = ExamAttempt.objects.filter(
        started_at__date=timezone.now().date()
    ).count()

    # ==========================
    # PAYMENTS
    # ==========================
    total_revenue = Transaction.objects.filter(
        verified=True,
    ).aggregate(total=Sum("amount"))["total"] or 0

    pending_orders = Order.objects.filter(status="pending").count()

    # ==========================
    # PTA
    # ==========================
    pending_pta = PTARequest.objects.filter(status="PENDING").count()

    # ==========================
    # PICKUPS
    # ==========================
    active_pickups = PickupAuthorization.objects.filter(
        is_used=False,
        expires_at__gt=timezone.now()
    ).count()

    context = {
        "stats": {
            "total_users": total_users,
            "pending_users": pending_users,
            "students": students,
            "parents": parents,
            "staff": staff,
            "total_exams": total_exams,
            "active_exams": active_exams,
            "attempts_today": attempts_today,
            "total_revenue": total_revenue,
            "pending_orders": pending_orders,
            "pending_pta": pending_pta,
            "active_pickups": active_pickups,
        }
    }

    return render(request, "exams/admin/admin_mega_dashboard.html", context)
