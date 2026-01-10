from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.core.mail import send_mail
from django.http import JsonResponse
from django.db.models import Sum
from payroll.models import ( 
    PaymentTransaction, PayrollRecord, Payee,
    StaffProfile, BankAccount, AuditLog, PaymentBatch,
    PayrollAuditLog, PayrollLineItem,  PayrollPeriod, PaymentBatch,
    Payee )
from payroll.forms import LeaveRequestForm
from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from payroll.models import PayrollPeriod
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.utils import timezone

from django.shortcuts import get_object_or_404, redirect, render
from django.utils.crypto import get_random_string

from .models import Payee, PayeeSalaryStructure, PayrollEnrollment
from .forms import PayrollEnrollmentForm
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count
from django.shortcuts import render

from django.conf import settings
from django.http import JsonResponse
from django.db.models import Sum
from payroll.models import PayrollRecord
from loans.models import Loan
from leaves.models import LeaveRequest

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from payroll.models import PayrollPeriod, PayrollRecord
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from payroll.models import (
    PayrollPeriod,
    PayrollRecord,
    Payee,
    AuditLog,
    PaymentBatch
)

from payroll.models import PayrollPeriod
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages

from .models import PaymentTransaction
from .services.payroll_generation import bulk_generate_payroll
from .services.payroll_engine import calculate_payroll
from .services.payment_batch_service import create_payment_batch
from .services.paystack_transfers import initiate_transfer
from .services.approval_service import approve_by_admin, approve_by_bursar
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from payroll.models import Payee, PayrollPeriod, PayrollRecord
from django.http import HttpResponseForbidden


User = get_user_model()


def is_staff(user):
    return user.role in ['ADMIN', 'TEACHER']


def notify_salary_paid(payroll_record):
    user = payroll_record.payee.linked_user
    if not user:
        return

    send_mail(
        "Salary Paid",
        f"Your salary for {payroll_record.payroll_period} has been paid.",
        "no-reply@school.com",
        [user.email],
    )


def send_sms(phone, message):
    # Plug Termii / Twilio here
    pass


@login_required
def approve_payroll_period(request, period_id):
    period = get_object_or_404(PayrollPeriod, id=period_id)

    if request.user.role not in ["ADMIN", "BURSAR"]:
        return HttpResponseForbidden()

    if not period.is_generated:
        messages.error(request, "Generate payroll before approval.")
        return redirect("payroll:payroll_period_detail", period.pk)

    period.is_approved = True
    period.approved_by = request.user
    period.approved_at = timezone.now()
    period.save()

    messages.success(request, "Payroll period approved.")
    return redirect("payroll:payroll_period_detail", period.pk)


@login_required
def lock_payroll_period(request, period_id):
    period = get_object_or_404(PayrollPeriod, id=period_id)

    if request.user.role != "ADMIN":
        messages.error(request, "Only admin can lock payroll.")
        return redirect("payroll:period_detail", period.pk)

    if not period.is_paid:
        messages.error(request, "Cannot lock unpaid payroll.")
        return redirect("payroll:period_detail", period.pk)

    period.is_locked = True
    period.save()

    messages.success(request, "Payroll period locked.")
    return redirect("payroll:period_detail", period.pk)


@login_required
def generate_payroll_for_period(request, period_id):
    period = get_object_or_404(PayrollPeriod, id=period_id)

    if period.is_locked:
        messages.error(request, "Payroll period is locked.")
        return redirect("payroll:period_detail", period.pk)

    try:
        result = bulk_generate_payroll(
            payroll_period=period,
            generated_by=request.user
        )
        period.is_generated = True
        period.save()

        messages.success(
            request,
            f"Payroll generated. Created: {result['created']}, Skipped: {result['skipped']}"
        )

    except Exception as e:
        messages.error(request, str(e))

    return redirect("payroll:payroll_period_detail", period.pk)



@login_required
def bursar_approve_payroll(request, record_id):
    record = get_object_or_404(PayrollRecord, id=record_id)

    try:
        approve_by_bursar(record, request.user)
        messages.success(request, "Payroll approved by Bursar.")
    except Exception as e:
        messages.error(request, str(e))

    return redirect("payroll:payroll_record_detail", record.id)



@login_required
def admin_approve_payroll(request, record_id):
    record = get_object_or_404(PayrollRecord, id=record_id)

    try:
        approve_by_admin(record, request.user)
        messages.success(request, "Payroll approved by Admin.")
    except Exception as e:
        messages.error(request, str(e))

    return redirect("payroll:payroll_record_detail", record.id)


@login_required
def create_payment_batch_view(request, period_id):
    period = get_object_or_404(PayrollPeriod, id=period_id)

    if request.user.role not in ["ADMIN", "BURSAR"]:
        messages.error(request, "Permission denied.")
        return redirect("payroll:period_detail", period.pk)

    if not period.is_approved:
        messages.error(request, "Payroll must be approved first.")
        return redirect("payroll:period_detail", period.pk)

    if period.is_paid:
        messages.warning(request, "Payroll already paid.")
        return redirect("payroll:period_detail", period.pk)

    batch = create_payment_batch(
        payroll_period=period,
        created_by=request.user
    )

    messages.success(
        request,
        f"Payment batch created with {batch.transactions.count()} transfers."
    )

    return redirect("payroll:batch_detail", batch.id)


@login_required
def payment_batch_detail(request, batch_id):
    batch = get_object_or_404(PaymentBatch, id=batch_id)

    transactions = batch.transactions.select_related(
        "payroll_record__payee"
    )

    has_pending = batch.transactions.filter(status="pending").exists()

    return render(
        request,
        "payroll/admin/bash_detail.html",
        {
            "batch": batch,
            "transactions": transactions,
            "has_pending": has_pending,
        }
    )



@login_required
def execute_payment_batch(request, batch_id):
    batch = get_object_or_404(PaymentBatch, id=batch_id)

    if request.user.role not in ["ADMIN", "BURSAR"]:
        messages.error(request, "Permission denied.")
        return redirect("payroll:batch_detail", batch.id)

    success = 0
    failed = 0

    for tx in batch.transactions.filter(status="pending"):
        initiate_transfer(tx)
        if tx.status == "success":
            success += 1
        else:
            failed += 1

    if failed == 0:
        batch.payroll_period.is_paid = True
        batch.payroll_period.save()

    messages.success(
        request,
        f"Transfers completed. Success: {success}, Failed: {failed}"
    )

    return redirect("payroll:batch_detail", batch.id)


@login_required
def retry_failed_transactions(request, batch_id):
    batch = get_object_or_404(PaymentBatch, id=batch_id)

    if request.user.role not in ["ADMIN", "BURSAR"]:
        messages.error(request, "Permission denied.")
        return redirect("payroll:batch_detail", batch.id)

    failed_txs = batch.transactions.filter(status="failed")
    success = 0
    failed = 0

    for tx in failed_txs:
        initiate_transfer(tx)
        if tx.status == "success":
            success += 1
        else:
            failed += 1

    # Mark payroll period as paid if all now succeed
    if batch.transactions.filter(status="pending").exists() == False and batch.transactions.filter(status="failed").exists() == False:
        batch.payroll_period.is_paid = True
        batch.payroll_period.save()

    messages.success(
        request,
        f"Retry completed. Success: {success}, Still Failed: {failed}"
    )
    return redirect("payroll:batch_detail", batch.id)


# =========================
# AUDIT LOGS
# =========================
@login_required
def audit_log_list(request):
    logs = AuditLog.objects.select_related("user").order_by("-created_at")
    return render(request, "payroll/admin/audit_log_list.html", {"logs": logs})



@login_required
def payroll_chart_data(request):
    payee = request.user.payee

    records = PayrollRecord.objects.filter(payee=payee).order_by("created_at")

    return JsonResponse({
        "labels": [r.payroll_period.name for r in records],
        "net_pay": [float(r.net_pay) for r in records],
        "deductions": [float(r.total_deductions) for r in records],
    })



def log_action(user, action, entity, entity_id=None, metadata=None):
    AuditLog.objects.create(
        user=user,
        action=action,
        entity=entity,
        entity_id=entity_id,
        metadata=metadata or {}
    )


@login_required
def payroll_dashboard(request):
    user = request.user
      
    # ADMIN / BURSAR
    if user.role in ["ADMIN", "BURSAR"]:
        # Latest payroll periods
        periods = PayrollPeriod.objects.order_by("-year", "-month")[:6]

        # Latest payment batches
        batches = PaymentBatch.objects.order_by("-created_at")[:10]

        context = {
            "periods": periods,
            "batches": batches,
        }
        return render(request, "payroll/admin/admin_dashboard.html", context)
    
    # STAFF (Teacher / Non-Teacher)
    payee = Payee.objects.get(user=user)

    context = {
        "payee": payee,
        "recent_payrolls": PayrollRecord.objects.filter(payee=payee)[:5],
        "active_loans": Loan.objects.filter(
            payee=payee,
            status="approved"
        ),
    }
    return render(request, "payroll/staff/dashboard.html", context)


@login_required
def admin_dashboard(request):
    user = request.user
    if user.role in ["ADMIN", "BURSAR"]:
        # Latest payroll periods
        periods = PayrollPeriod.objects.order_by("-year", "-month")[:6]

        # Include transactions info
        batches = []
        for batch in PaymentBatch.objects.order_by("-created_at")[:10]:
            tx_pending = batch.transactions.filter(status="pending").count()
            tx_failed = batch.transactions.filter(status="failed").count()
            batches.append({
                "batch": batch,
                "pending_count": tx_pending,
                "failed_count": tx_failed,
            })

        context = {
            "periods": periods,
            "batches": batches,
        }   
        return render(request, "payroll/admin/admin_dashboard.html", context)
    
    # STAFF (Teacher / Non-Teacher)
    payee = Payee.objects.get(user=user)

    context = {
        "payee": payee,
        "recent_payrolls": PayrollRecord.objects.filter(payee=payee)[:5],
        "active_loans": Loan.objects.filter(
            payee=payee,
            status="approved"
        ),
    }
    return render(request, "payroll/staff/dashboard.html", context)

# =========================
# PAYROLL PERIODS
# =========================
from django.db import models 
from django.db.models import Count
from payroll.models import PayrollPeriod, PayrollRecord

@login_required
def create_payroll_period(request):
    if request.user.role not in ["ADMIN", "BURSAR"]:
        messages.error(request, "Permission denied.")
        return redirect("payroll:period_list")

    if request.method == "POST":
        month = int(request.POST.get("month"))
        year = int(request.POST.get("year"))

        period, created = PayrollPeriod.objects.get_or_create(
            month=month,
            year=year
        )

        if not created:
            messages.warning(request, "Payroll period already exists.")
        else:
            messages.success(request, "Payroll period created successfully.")

        return redirect("payroll:period_detail", period.pk)

    return render(request, "payroll/admin/period_create.html")



@login_required
def payroll_period_list(request):
    periods = PayrollPeriod.objects.order_by("-year", "-month")

    return render(
        request,
        "payroll/admin/period_list.html",
        {"periods": periods}
    )


@login_required
def payroll_period_detail(request, period_id):
    period = get_object_or_404(PayrollPeriod, id=period_id)

    records = PayrollRecord.objects.filter(
        payroll_period=period
    ).select_related("payee")

    context = {
        "period": period,
        "records": records,
    }

    return render(
        request,
        "payroll/admin/period_detail.html",
        context
    )


# =========================
# PAYROLL RECORDS
# =========================
@login_required
def payroll_record_list(request):
    records = PayrollRecord.objects.select_related("payee", "period")
    return render(request, "payroll/admin/record_list.html", {"records": records})


@login_required
def payroll_record_detail(request, pk):
    record = get_object_or_404(PayrollRecord, pk=pk)
    return render(request, "payroll/admin/record_detail.html", {"record": record})


# =========================
# PAYEES
# =========================
@login_required
def payee_list(request):
    payees = Payee.objects.select_related("user")
    return render(request, "payroll/admin/payee_list.html", {"payees": payees})


@login_required
def payee_detail(request, pk):
    payee = get_object_or_404(Payee, pk=pk)
    records = PayrollRecord.objects.filter(payee=payee)
    return render(request, "payroll/admin/payee_detail.html", {
        "payee": payee,
        "records": records,
    })




def payroll_summary(period):
    qs = PayrollRecord.objects.filter(payroll_period=period)
    return {
        "gross": qs.aggregate(Sum("gross_pay"))["gross_pay__sum"] or 0,
        "net": qs.aggregate(Sum("net_pay"))["net_pay__sum"] or 0,
        "deductions": qs.aggregate(
            Sum("total_deductions")
        )["total_deductions__sum"] or 0,
    }


def notify_leave_status(leave):
    send_mail(
        "Leave Request Update",
        f"Your leave request is {leave.status}.",
        "no-reply@school.com",
        [leave.staff.payee.linked_user.email],
    )



@login_required
def staff_payslip_dashboard(request):
    payee = get_object_or_404(Payee, user=request.user)

    payrolls = (
        PayrollRecord.objects
        .filter(payee=payee)
        .select_related("payroll_period")
        .order_by("-payroll_period__year", "-payroll_period__month")
    )

    return render(
        request,
        "payroll/staff/payslip_dashboard.html",
        {
            "payrolls": payrolls,
            "payee": payee,
        }
    )


@login_required
def payslip_pdf_view(request, payroll_id):
    payroll = get_object_or_404(PayrollRecord, id=payroll_id)

    # SECURITY: staff can only access their own
    if payroll.payee.user != request.user and not request.user.is_superuser:
        return HttpResponse("Unauthorized", status=403)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="Payslip_{payroll.payroll_period.month}_{payroll.payroll_period.year}.pdf"'
    )

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    y = height - 50

    def draw(text, offset=20):
        nonlocal y
        p.drawString(50, y, text)
        y -= offset

    # HEADER
    p.setFont("Helvetica-Bold", 16)
    draw("PAYSLIP", 30)

    p.setFont("Helvetica", 11)
    draw(f"Name: {payroll.payee.full_name}")
    draw(f"Period: {payroll.payroll_period.month}/{payroll.payroll_period.year}")
    draw(f"Payee Type: {payroll.payee.payee_type}")

    draw("-" * 80, 25)

    # PAY DETAILS
    draw(f"Gross Pay: ₦{payroll.gross_pay}")
    draw(f"Total Deductions: ₦{payroll.total_deductions}")
    draw(f"Net Pay: ₦{payroll.net_pay}", 30)

    draw("-" * 80, 25)

    draw("This is a system-generated payslip.", 30)

    p.showPage()
    p.save()

    return response



@login_required
def staff_bank_account_update(request):
    payee = get_object_or_404(Payee, user=request.user)

    bank = payee.bank_accounts.filter(is_primary=True).first()

    if request.method == "POST":
        BankAccount.objects.update_or_create(
            payee=payee,
            is_primary=True,
            defaults={
                "bank_name": request.POST["bank_name"],
                "account_number": request.POST["account_number"],
                "account_name": request.POST["account_name"],
            },
        )
        return redirect("staff_dashboard")

    return render(
        request,
        "payroll/staff/bank_account_form.html",
        {"bank": bank},
    )



@login_required
def staff_bank_account_submit(request):
    payee = get_object_or_404(Payee, user=request.user)

    if request.method == "POST":
        BankAccount.objects.create(
            payee=payee,
            bank_name=request.POST["bank_name"],
            account_number=request.POST["account_number"],
            account_name=request.POST["account_name"],
            is_primary=True,
            is_approved=False,
        )
        return JsonResponse({"success": True})

    return render(
        request,
        "payroll/staff/bank_account_form.html"
    )



@login_required
def approve_bank_account(request, account_id):
    if not request.user.is_superuser:
        return HttpResponse(status=403)

    account = get_object_or_404(BankAccount, id=account_id)

    account.is_approved = True
    account.approved_by = request.user
    account.approved_at = timezone.now()
    account.save()

    PayrollAuditLog.objects.create(
        action="Approved bank account",
        performed_by=request.user,
        metadata={"account_id": account.id}
    )

    return redirect("admin_bank_accounts")



@login_required
def monthly_payroll_chart(request):
    if not request.user.is_superuser:
        return HttpResponse(status=403)

    data = (
        PayrollRecord.objects
        .values("payroll_period__month", "payroll_period__year")
        .annotate(total=Sum("net_pay"))
        .order_by("payroll_period__year", "payroll_period__month")
    )

    return JsonResponse(list(data), safe=False)


@login_required
def monthly_deductions_chart(request):
    if not request.user.is_superuser:
        return JsonResponse([], safe=False)

    data = (
        PayrollRecord.objects
        .filter(paymenttransaction__status="SUCCESS")
        .values("payroll_period__year", "payroll_period__month")
        .annotate(total=Sum("total_deductions"))
        .order_by("payroll_period__year", "payroll_period__month")
    )

    return JsonResponse([
        {
            "month": f'{d["payroll_period__year"]}-{str(d["payroll_period__month"]).zfill(2)}',
            "total": float(d["total"]),
        }
        for d in data
    ], safe=False)



@login_required
def deduction_dashboard(request):
    if not request.user.is_superuser:
        return HttpResponse(status=403)

    records = (
        PayrollLineItem.objects
        .select_related("component", "payroll_record__payroll_period")
        .order_by(
            "-payroll_record__payroll_period__year",
            "-payroll_record__payroll_period__month"
        )
    )

    return render(
        request,
        "payroll/admin/deduction_dashboard.html",
        {"records": records}
    )


@login_required
def deduction_breakdown_chart(request):
    data = (
        PayrollLineItem.objects
        .filter(line_type="deduction")
        .values(
            "component__name",
            "payroll_record__payroll_period__year",
            "payroll_record__payroll_period__month"
        )
        .annotate(total=Sum("amount"))
        .order_by(
            "payroll_record__payroll_period__year",
            "payroll_record__payroll_period__month"
        )
    )

    return JsonResponse(list(data), safe=False)


@login_required
def staff_salary_history(request):
    records = PayrollRecord.objects.filter(
        payee__user=request.user
    ).order_by("-payroll_period__month")

    return render(request, "payroll/staff/salary_history.html", {
        "records": records
    })



@staff_member_required
def salary_detail(request, pk):
    payee = get_object_or_404(Payee, pk=pk)

    loans = Loan.objects.filter(payee=payee).order_by("-created_at")
    payrolls = PayrollRecord.objects.filter(payee=payee).order_by("-created_at")

    context = {
        "payee": payee,
        "loans": loans,
        "payrolls": payrolls,
    }
    return render(request, "payroll/payee_detail.html", context)




def staff_salary_chart(request):
    payee = Payee.objects.get(user=request.user)

    data = (
        PayrollRecord.objects
        .filter(payee=payee, status="approved")
        .values("payroll_period__month", "payroll_period__year")
        .annotate(
            gross=Sum("gross_pay"),
            deductions=Sum("total_deductions"),
        )
        .order_by("payroll_period__year", "payroll_period__month")
    )

    return JsonResponse([
        {
            "label": f"{d['payroll_period__month']}/{d['payroll_period__year']}",
            "gross": float(d["gross"]),
            "deductions": float(d["deductions"]),
            "net": float(d["gross"] - d["deductions"]),
        }
        for d in data
    ], safe=False)




@staff_member_required
def enroll_user_to_payroll(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if hasattr(user, "payee"):
        return redirect("payroll:payee_detail", user.payee.id)

    if request.method == "POST":
        form = PayrollEnrollmentForm(request.POST)
        if form.is_valid():
            payee = Payee.objects.create(
                user=user,
                full_name=form.cleaned_data["full_name"],
                payee_type=form.cleaned_data["payee_type"],
                reference_code=f"{user.first_name} - get_random_string(10).upper()",
            )

            PayeeSalaryStructure.objects.create(
                payee=payee,
                salary_structure=form.cleaned_data["salary_structure"],
                assigned_by=request.user,
            )

            PayrollEnrollment.objects.create(
                user=user,
                payee=payee,
                enrolled_by=request.user,
            )

            return redirect("payroll:payee_detail", payee.id)
    else:
        form = PayrollEnrollmentForm(
            initial={"full_name": user.get_full_name()}
        )

    return render(request, "payroll/staff/enroll.html", {"form": form, "user": user})


def register_payroll(self, request, user_id):
    user = get_object_or_404(User, id=user_id)

    PAYROLL_ELIGIBLE_ROLES = {
        "ADMIN": "admin",
        "TEACHER": "teacher",
        "NON_TEACHER": "non_teacher",
    }

    if user.role not in PAYROLL_ELIGIBLE_ROLES:
        messages.error(request, "This user cannot be registered to payroll.")
        return redirect(request.META.get("HTTP_REFERER"))

    payee_type = PAYROLL_ELIGIBLE_ROLES[user.role]

    payee, created = Payee.objects.get_or_create(
        user=user,
        defaults={
            "full_name": user.get_full_name(),
            "payee_type": payee_type,
            "reference_code": f"{user.first_name[:3]}-{get_random_string(10).upper()}",
        },
    )

    StaffProfile.objects.get_or_create(
        payee=payee,
        defaults={
            "phone_number": user.phone_number or "",
            "date_of_employment": user.created_at.date(),
            "is_confirmed": True,
        },
    )

    messages.success(request, "User successfully registered to payroll.")
    return redirect(f"/admin/users/user/{user.id}/change/")


