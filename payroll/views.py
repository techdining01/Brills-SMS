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
from .services.audit import log_action
from .services.payroll_engine import calculate_payroll
from .services.payment_batch_service import create_payment_batch
from .services.paystack_transfers import initiate_transfer
from .services.approval_service import approve_by_admin, approve_by_bursar



User = get_user_model()


def is_staff(user):
    return User.role in ['ADMIN', 'TEACHER']


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
def generate_payroll_bulk(request, period_id):
    period = get_object_or_404(PayrollPeriod, id=period_id)

    if request.method == "POST":
        result = bulk_generate_payroll(
            payroll_period=period,
            generated_by=request.user
        )

        messages.success(
            request,
            f"Payroll generated. Created: {result['created']}, Skipped: {result['skipped']}"
        )
        return redirect("payroll:payroll_period_detail", period.id)

    return render(request, "payroll/generate_bulk_confirm.html", {
        "period": period
    })



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

    try:
        batch = create_payment_batch(
            payroll_period=period,
            created_by=request.user
        )
        messages.success(request, "Payment batch created.")
        return redirect("payroll:payment_batch_detail", batch.id)

    except Exception as e:
        messages.error(request, str(e))
        return redirect("payroll:payroll_period_detail", period.id)



@login_required
def run_paystack_transfer(request, transaction_id):
    tx = get_object_or_404(PaymentTransaction, id=transaction_id)

    initiate_transfer(tx)

    if tx.status == "success":
        messages.success(request, "Transfer successful.")
    else:
        messages.error(request, "Transfer failed.")

    return redirect("payroll:payment_batch_detail", tx.batch.id)



# =========================
# ENTRY DASHBOARD
# =========================
@login_required
def payroll_dashboard(request):
    user = request.user

    if user.role in ["ADMIN", "BURSAR"]:
        return redirect("payroll:admin_dashboard")

    payee = get_object_or_404(Payee, user=user)
    return render(request, "payroll/staff/dashboard.html", {
        "payee": payee,
    })


# =========================
# ADMIN DASHBOARD
# =========================
@login_required
def admin_dashboard(request):
    context = {
        "payee_count": Payee.objects.count(),
        "period_count": PayrollPeriod.objects.count(),
        "pending_records": PayrollRecord.objects.filter(status="pending").count(),
    }
    return render(request, "payroll/admin/dashboard.html", context)


# =========================
# PAYROLL PERIODS
# =========================
@login_required
def period_list(request):
    periods = PayrollPeriod.objects.all().order_by("-start_date")
    return render(request, "payroll/admin/period_list.html", {"periods": periods})


@login_required
def period_detail(request, pk):
    period = get_object_or_404(PayrollPeriod, pk=pk)
    records = PayrollRecord.objects.filter(period=period)
    return render(request, "payroll/admin/period_detail.html", {
        "period": period,
        "records": records,
    })


# =========================
# PAYROLL RECORDS
# =========================
@login_required
def record_list(request):
    records = PayrollRecord.objects.select_related("payee", "period")
    return render(request, "payroll/admin/record_list.html", {"records": records})


@login_required
def record_detail(request, pk):
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


# =========================
# PAYROLL BATCH
# =========================
@login_required
def batch_detail(request, pk):
    batch = get_object_or_404(PaymentBatch, pk=pk)
    records = PayrollRecord.objects.filter(batch=batch)
    return render(request, "payroll/admin/batch_detail.html", {
        "batch": batch,
        "records": records,
    })


# =========================
# AUDIT LOGS
# =========================
@login_required
def audit_log_list(request):
    logs = AuditLog.objects.select_related("actor").order_by("-created_at")
    return render(request, "payroll/admin/audit_log_list.html", {"logs": logs})



# @login_required
# def staff_loan_payroll_dashboard(request):
#     payee = Payee.objects.filter(user=request.user).order_by('payee_type').first()

#     return render(request, "payroll/staff/dashboard.html", {
#         "payslips": PayrollRecord.objects.filter(payee=payee),
#         "loans": Loan.objects.filter(payee=payee).prefetch_related("repayments"),
#         "leaves": LeaveRequest.objects.filter(staff__payee=payee),
#     })



# @login_required
# @user_passes_test(lambda u: u.role == "ADMIN")
# def admin_loan_payroll_dashboard(request):
#     return render(request, "payroll/admin/payroll_dashboard.html", {
#         "periods": PayrollPeriod.objects.all(),
#         "pending_loans": Loan.objects.filter(status="pending"),
#         "batches": PaymentBatch.objects.all(),
#     })




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
def payment_batch_detail(request, batch_id):
    batch = get_object_or_404(PaymentBatch, id=batch_id)

    transactions = batch.transactions.select_related(
        "payroll_record__payee"
    )

    return render(request, "payroll/admin/batch_detail.html", {
        "batch": batch,
        "transactions": transactions,
    })


@login_required
def retry_payment(request, tx_id):
    tx = get_object_or_404(
        PaymentTransaction,
        id=tx_id,
        status="failed"
    )

    tx.status = "pending"
    tx.save()

    log_action(
        user=request.user,
        action="RETRY",
        obj=tx,
        description="Manual retry initiated"
    )

    return redirect("payroll:payment_batch_detail", tx.batch.id)



@login_required
def generate_payroll_view(request, period_id):
    if not request.user.is_superuser:
        raise PermissionDenied("You are not allowed to generate payroll")

    period = get_object_or_404(PayrollPeriod, id=period_id)

    if period.is_locked():
        messages.error(request, "This payroll period is locked and cannot be regenerated.")
        return redirect("payroll_period_list")

    if request.method == "POST":
        result = bulk_generate_payroll(
            payroll_period=period,
            generated_by=request.user
        )

        return render(
            request,
            "payroll/admin/generate_payroll_result.html",
            {
                "period": period,
                "result": result,
            }
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
@staff_member_required
def admin_payroll_dashboard(request):
    stats = {
        "payees": Payee.objects.count(),
        "pending": PayrollRecord.objects.filter(status="pending").count(),
        "approved": PayrollRecord.objects.filter(status="approved").count(),
        "total_net": PayrollRecord.objects.aggregate(
            total=Sum("net_pay")
        )["total"] or 0,
        "batches": PaymentBatch.objects.count(),
    }

    recent_payrolls = (
        PayrollRecord.objects
        .select_related("payee", "payroll_period")
        .order_by("-created_at")[:8]
    )

    periods = PayrollPeriod.objects.order_by("-year", "-month")[:6]

    return render(
        request,
        "payroll/admin/dashboard.html",
        {
            "stats": stats,
            "recent_payrolls": recent_payrolls,
            "periods": periods,
        }
    )



@login_required
def staff_payroll_dashboard(request):
    # Get payee linked to logged-in user
    payee = get_object_or_404(Payee, user=request.user)

    payrolls = (
        PayrollRecord.objects
        .filter(payee=payee)
        .select_related("payroll_period")
        .order_by("-payroll_period__year", "-payroll_period__month")
    )

    total_paid = payrolls.filter(
        paymenttransaction__status="SUCCESS"
    ).aggregate(total=Sum("net_pay"))["total"] or 0

    latest_payroll = payrolls.first()

    context = {
        "payee": payee,
        "payrolls": payrolls[:6],
        "total_paid": total_paid,
        "latest": latest_payroll,
    }

    return render(request, "payroll/staff/dashboard.html", context)



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




# ======================================================================= #


from django.contrib import admin, messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import path
from django.utils.crypto import get_random_string
from accounts.models import User
from payroll.models import Payee, StaffProfile, SalaryStructure, PayeeSalaryStructure


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
            "reference_code": get_random_string(12).upper(),
        },
    )

    StaffProfile.objects.get_or_create(
        payee=payee,
        defaults={
            "phone_number": user.phone_number or "",
            "date_of_employment": user.created_at.date(),
        },
    )

    messages.success(request, "User successfully registered to payroll.")
    return redirect(f"/admin/users/user/{user.id}/change/")




@login_required
def create_payment_batch(request, period_id):
    period = get_object_or_404(PayrollPeriod, id=period_id)

    batch = PaymentBatch.objects.create(
        payroll_period=period,
        created_by=request.user
    )

    for record in PayrollRecord.objects.filter(payroll_period=period, status="approved"):
        bank = record.payee.bank_accounts.filter(is_primary=True).first()

        PaymentTransaction.objects.create(
            payroll_record=record,
            batch=batch,
            amount=record.net_pay,
            bank_name=bank.bank_name,
            account_number=bank.account_number,
            account_name=bank.account_name,
        )

    messages.success(request, "Payment batch created.")
    return redirect("admin_batch_detail", batch.id)


import requests

PAYSTACK_BASE = "https://api.paystack.co"

def paystack_transfer(amount, recipient_code):
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "source": "balance",
        "amount": int(amount * 100),
        "recipient": recipient_code,
        "reason": "Salary Payment"
    }

    response = requests.post(
        f"{PAYSTACK_BASE}/transfer",
        json=payload,
        headers=headers
    )

    return response.json()


def execute_batch_payment(batch):
    for tx in batch.transactions.all():
        res = paystack_transfer(tx.amount, tx.recipient_code)

        if res.get("status"):
            tx.status = "success"
        else:
            tx.status = "failed"

        tx.raw_response = res
        tx.save()


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
