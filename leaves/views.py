from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect

from loans.models import LoanApplication
from .models import LeaveRequest, LeaveType
from payroll.models import Payee
from django.utils import timezone
from django.contrib import messages
from leaves.services import has_overlapping_leave
from datetime import timedelta
from django.http import JsonResponse
from payroll.models import PayrollPeriod
from django.utils import timezone
from django.contrib import messages
from leaves.services import calculate_leave_balance

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib import messages

from leaves.models import LeaveRequest


# dashboard/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.core.paginator import Paginator
from payroll.models import PayrollPeriod
from loans.models import Loan
from leave.models import LeaveRequest




@login_required
def admin_dashboard(request):
    pending_periods = PayrollPeriod.objects.filter(
        is_generated=True, is_approved=False
    ).order_by("-year", "-month")

    pending_loans = Loan.objects.filter(status="pending").order_by("-created_at")
    pending_leaves = LeaveRequest.objects.filter(status="pending").order_by("-start_date")

    context = {
        "pending_periods": Paginator(pending_periods, 5).get_page(
            request.GET.get("p_periods")
        ),
        "pending_loans": Paginator(pending_loans, 5).get_page(
            request.GET.get("p_loans")
        ),
        "pending_leaves": Paginator(pending_leaves, 5).get_page(
            request.GET.get("p_leaves")
        ),
    }
    return render(request, "dashboard/admin_dashboard.html", context)



@login_required
def staff_dashboard(request):
    payee = request.user.payee

    leaves = LeaveRequest.objects.filter(payee=payee).order_by("-start_date")
    balance = calculate_leave_balance(payee)

    context = {
        "leave_balance": balance,
        "leaves": Paginator(leaves, 5).get_page(
            request.GET.get("page")
        ),
    }
    return render(request, "dashboard/staff_dashboard.html", context)



@login_required
def leave_balance_view(request):
    year = timezone.now().year
    balances = []

    for lt in LeaveType.objects.all():
        balances.append({
            "type": lt,
            **calculate_leave_balance(request.user.payee, lt, year)
        })

    return render(
        request,
        "leave/staff/leave_balance.html",
        {"balances": balances, "year": year}
    )



@login_required
def request_leave(request):
    payee = request.user.payee

    if request.method == "POST":
        start = request.POST["start_date"]
        end = request.POST["end_date"]

        if has_overlapping_leave(payee, start, end):
            messages.error(request, "You already have a leave in this period.")
            return redirect("leaves:request")

        LeaveRequest.objects.create(
            payee=payee,
            leave_type_id=request.POST["leave_type"],
            start_date=start,
            end_date=end,
            reason=request.POST["reason"],
        )

        messages.success(request, "Leave request submitted.")
        return redirect("leaves:staff_dashboard")

    return render(request, "leaves/staff/leave_request.html")




@login_required
def dashboard_router(request):
    if request.user.role in ["ADMIN", "BURSAR"]:
        return redirect("dashboard:admin_dashboard")
    return redirect("dashboard:staff_dashboard")



# @login_required
# def admin_leave_dashboard(request):
#     if request.user.role not in ["ADMIN", "BURSAR"]:
#         messages.error(request, "Permission denied")
#         return redirect("dashboard")

#     qs = LeaveRequest.objects.select_related(
#         "payee", "leave_type"
#     ).order_by("-created_at")

#     paginator = Paginator(qs, 15)
#     page = request.GET.get("page")
#     leaves = paginator.get_page(page)

#     return render(
#         request,
#         "leave/admin/admin_leave_dashboard.html",
#         {"leaves": leaves},
#     )



@login_required
def approve_leave(request, leave_id):
    leave = get_object_or_404(LeaveRequest, id=leave_id)

    year = leave.start_date.year
    balance = calculate_leave_balance(
        leave.payee, leave.leave_type, year
    )

    if leave.duration() > balance["remaining"]:
        messages.error(
            request,
            f"Insufficient leave balance. Remaining: {balance['remaining']} days"
        )
        return redirect("leave:admin_dashboard")

    leave.status = "approved"
    leave.reviewed_by = request.user
    leave.reviewed_at = timezone.now()
    leave.save()

    messages.success(request, "Leave approved successfully.")
    return redirect("leave:admin_dashboard")



@login_required
def reject_leave(request, leave_id):
    leave = get_object_or_404(LeaveRequest, id=leave_id)

    leave.status = "rejected"
    leave.reviewed_by = request.user
    leave.reviewed_at = timezone.now()
    leave.save()

    messages.success(request, "Leave rejected.")
    return redirect("leave:admin_dashboard")


@login_required
def leave_history(request):
    qs = LeaveRequest.objects.all().order_by("-start_date")

    if request.user.role not in ["ADMIN", "BURSAR"]:
        qs = qs.filter(payee=request.user.payee)

    page = Paginator(qs, 10).get_page(request.GET.get("page"))

    return render(request, "leave/leave_history.html", {"page": page})



@login_required
def leave_heatmap(request):
    leaves = LeaveRequest.objects.filter(status="approved")

    data = {}
    for l in leaves:
        day = l.start_date.strftime("%Y-%m")
        data[day] = data.get(day, 0) + l.days

    return render(
        request,
        "leave/leave_heatmap.html",
        {"data": data}
    )



@login_required
def leave_calendar_feed(request):
    qs = LeaveRequest.objects.filter(status="approved")

    if request.user.role not in ["ADMIN", "BURSAR"]:
        qs = qs.filter(payee=request.user.payee)

    data = [
        {
            "title": lr.payee.full_name,
            "start": lr.start_date.isoformat(),
            "end": lr.end_date.isoformat(),
        }
        for lr in qs
    ]

    return JsonResponse(data, safe=False)


from django.utils.timezone import now

@login_required
def leave_calendar(request):
    year = now().year
    leaves = LeaveRequest.objects.filter(
        start_date__year=year
    ).select_related("payee")

    return render(
        request,
        "leaves/leave_calendar.html",
        {"leaves": leaves}
    )


import csv
from django.http import HttpResponse

@login_required
def export_leave_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="leave_report.csv"'

    writer = csv.writer(response)
    writer.writerow(["Staff", "From", "To", "Days", "Status"])

    for l in LeaveRequest.objects.all():
        writer.writerow([
            l.payee, l.start_date, l.end_date, l.days, l.status
        ])

    return response

