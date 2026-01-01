from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from payroll.models import PayrollRecord, StaffProfile
from payroll.services.payslip_pdf import generate_payslip_pdf
from django.http import HttpResponse
from django.core.mail import send_mail
from payroll.models import Payroll
from django.http import JsonResponse
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from payroll.models import PaymentTransaction
from payroll.models import PayrollRecord



@login_required
def staff_salary_history(request):
    records = PayrollRecord.objects.filter(
        payee__user=request.user
    ).order_by("-payroll_period__month")

    return render(request, "payroll/staff/salary_history.html", {
        "records": records
    })



@login_required
def staff_download_payslip(request, pk):
    record = PayrollRecord.objects.get(
        id=pk, payee__linked_user=request.user
    )
    pdf = generate_payslip_pdf(record)

    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = "attachment; filename=payslip.pdf"
    return response


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
def staff_dashboard(request):
    profile = StaffProfile.objects.get(
        payee__linked_user=request.user
    )
    payrolls = PayrollRecord.objects.filter(
        payee=profile.payee
    ).order_by("-created_at")[:6]

    return render(request, "staff/dashboard.html", {
        "profile": profile,
        "payrolls": payrolls,
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
def monthly_payroll_chart(request):
    data = (
        PaymentTransaction.objects
        .filter(status=PaymentTransaction.Status.SUCCESS)
        .values('payroll_record__payroll_period__month')
        .annotate(total=Sum('amount'))
        .order_by('payroll_record__payroll_period__month')
    )

    return JsonResponse([
        {
            "month": item["payroll_record__payroll_period__month"].strftime("%Y-%m"),
            "total": float(item["total"]),
        }
        for item in data
    ], safe=False)



@login_required
def monthly_deductions_chart(request):
    data = (
        PayrollRecord.objects
        .filter(paymenttransaction__status='SUCCESS')
        .values('payroll_period__month')
        .annotate(total=Sum('total_deductions'))
        .order_by('payroll_period__month')
    )

    return JsonResponse([
        {
            "month": d["payroll_period__month"].strftime("%Y-%m"),
            "total": float(d["total"]),
        }
        for d in data
    ], safe=False)



@login_required
def staff_salary_history(request):
    records = PayrollRecord.objects.filter(
        payee__user=request.user
    ).order_by("-payroll_period__month")

    return render(request, "payroll/staff/salary_history.html", {
        "records": records
    })



from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from payroll.models import PaymentBatch

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


# payroll/views/payslip.py
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from weasyprint import HTML
from django.http import HttpResponse
from payroll.models import PayrollRecord
from django.contrib.auth.decorators import login_required

@login_required
def payslip_pdf(request, record_id):
    record = get_object_or_404(
        PayrollRecord,
        id=record_id,
        payee__user=request.user
    )

    html = render_to_string("payroll/staff/payslip_pdf.html", {
        "record": record
    })

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = "inline; filename=payslip.pdf"

    HTML(string=html).write_pdf(response)
    return response



# payroll/views/payments.py
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from payroll.models import PaymentTransaction
from payroll.services.audit import log_action

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


# payroll/views/staff_leave.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from payroll.models import LeaveRequest, AuditLog
from payroll.forms import LeaveRequestForm
from payroll.services.audit import log_action

# payroll/views/staff_leave.py
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
    leaves = LeaveRequest.objects.filter(staff=request.user).order_by("-applied_at")
    return render(request, "payroll/staff/ajax_leave_history.html", {"leaves": leaves})


# payroll/views/payroll_generation.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied

from payroll.models import PayrollPeriod
from payroll.services.payroll_generation import bulk_generate_payroll


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

    return render(
        request,
        "payroll/admin/generate_payroll_confirm.html",
        {
            "period": period
        }
    )
