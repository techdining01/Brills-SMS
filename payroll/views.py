from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.core.mail import send_mail
from django.http import JsonResponse
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from payroll.models import PaymentTransaction, PayrollRecord, Payee, StaffProfile, BankAccount, LeaveRequest, AuditLog, PaymentBatch, PayrollAuditLog, PayrollLineItem
from payroll.forms import LeaveRequestForm
from payroll.services.audit import log_action
from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from payroll.models import PayrollPeriod
from payroll.services.payroll_generation import bulk_generate_payroll
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.utils import timezone



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
def staff_salary_history(request):
    records = PayrollRecord.objects.filter(
        payee__user=request.user
    ).order_by("-payroll_period__month")

    return render(request, "payroll/staff/salary_history.html", {
        "records": records
    })




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
def staff_apply_leave(request):
    staff = request.user.staffprofile

    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.staff = staff
            leave.save()

            AuditLog.objects.create(
                user=request.user,
                action="LEAVE_APPLIED",
                description=f"{leave.leave_type} {leave.start_date} → {leave.end_date}"
            )

            return JsonResponse({"ok": True})

        return JsonResponse({"ok": False, "errors": form.errors})

    return render(request, "payroll/staff/leave_apply.html", {
        "form": LeaveRequestForm(),
        "leaves": LeaveRequest.objects.filter(staff=staff).order_by("-applied_at")
    })


@login_required
def staff_leave_history(request):
    staff = get_object_or_404(StaffProfile, id=request.user.id)
    leaves = LeaveRequest.objects.filter(staff=staff).order_by("-applied_at")
    return render(request, "payroll/staff/ajax_leave_history.html", {"leaves": leaves})



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


from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count
from django.shortcuts import render
from payroll.models import (
    PayrollRecord,
    PayrollPeriod,
    PaymentBatch,
    Payee
)



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


