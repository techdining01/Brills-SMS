from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Loan, LoanRepayment, LoanSchedule
from decimal import Decimal
from payroll.models import PayrollLineItem, SalaryComponent, PayrollRecord, PayrollPeriod, PaymentBatch
from leaves.models import LeaveRequest
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from payroll.models import AuditLog
from django.conf import settings


@login_required
def request_loan(request):
    payee = request.user.payee

    if request.method == "POST":
        principal = Decimal(request.POST["amount"])
        months = int(request.POST["months"])
        monthly = principal / months

        Loan.objects.create(
            payee=payee,
            principal=principal,
            months=months,
            monthly_deduction=monthly
        )
        messages.success(request, "Loan request submitted.")
        return redirect("staff:loan_dashboard")

    return render(request, "staff/loan_request.html")


@login_required
@user_passes_test(lambda u: u.role == "ADMIN")
def approve_loan(request, loan_id):
    loan = get_object_or_404(Loan, id=loan_id, status="pending")
    loan.status = "approved"
    loan.approved_by = request.user
    loan.save()
    messages.success(request, "Loan approved.")
    return redirect("admin_loan_list")



def apply_loans(payee, payroll_record):
    loans = Loan.objects.filter(payee=payee, status="approved")

    for loan in loans:
        LoanRepayment.objects.create(
            loan=loan,
            payroll_record=payroll_record,
            amount=loan.monthly_deduction
        )

        PayrollLineItem.objects.create(
            payroll_record=payroll_record,
            component=SalaryComponent.objects.get(name="Loan Deduction"),
            line_type="deduction",
            amount=loan.monthly_deduction,
            metadata={"loan_id": loan.id}
        )




@login_required
def staff_loan_payroll_dashboard(request):
    payee = request.user.payee

    return render(request, "loans/staff/dashboard.html", {
        "payslips": PayrollRecord.objects.filter(payee=payee),
        "loans": Loan.objects.filter(payee=payee).prefetch_related("repayments"),
        "leaves": LeaveRequest.objects.filter(staff__payee=payee),
    })


@login_required
@user_passes_test(lambda u: u.role == "ADMIN")
def admin_loan_payroll_dashboard(request):
    return render(request, "loans/admin/loan_payroll_dashboard.html", {
        "periods": PayrollPeriod.objects.all(),
        "pending_loans": Loan.objects.filter(status="pending"),
        "batches": PaymentBatch.objects.all(),
    })



def apply_loan_deduction(payee, payroll):
    schedules = LoanSchedule.objects.filter(
        loan__payee=payee,
        paid=False
    ).order_by("month")

    if schedules.exists():
        schedule = schedules.first()
        payroll.add_deduction(
            "Loan Repayment",
            schedule.total_payment
        )
        schedule.paid = True
        schedule.save()



@staff_member_required
def admin_loans_list(request):
    loans = Loan.objects.select_related("payee").order_by("-requested_at")

    status = request.GET.get("status")
    if status:
        loans = loans.filter(status=status)

    return render(
        request,
        "payroll/admin/loan_list.html",
        {
            "loans": loans,
            "status": status,
        },
    )


@staff_member_required
def approve_loan(request, loan_id):
    loan = get_object_or_404(Loan, id=loan_id)

    if loan.status != "pending":
        return redirect("admin_loans")

    loan.status = "approved"
    loan.approved_by = request.user
    loan.approved_at = timezone.now()
    loan.save()

    AuditLog.objects.create(
        user=request.user,
        action="APPROVE",
        object_type="Loan",
        object_id=str(loan.id),
        description=f"Approved loan for {loan.payee.full_name}",
    )

    return redirect("admin_loans")



@staff_member_required
def reject_loan(request, loan_id):
    loan = get_object_or_404(Loan, id=loan_id)

    if loan.status != "pending":
        return redirect("admin_loans")

    loan.status = "rejected"
    loan.save()

    AuditLog.objects.create(
        user=request.user,
        action="FAIL",
        object_type="Loan",
        object_id=str(loan.id),
        description=f"Rejected loan for {loan.payee.full_name}",
    )

    return redirect("admin_loans")


@staff_member_required
def loan_amortization_table(request, loan_id):
    loan = get_object_or_404(Loan, id=loan_id)

    total_interest = (
        loan.amount * loan.interest_rate / Decimal("100")
    )
    total_payable = loan.amount + total_interest
    monthly_payment = total_payable / loan.duration_months

    schedule = []
    balance = total_payable

    for month in range(1, loan.duration_months + 1):
        balance -= monthly_payment
        schedule.append(
            {
                "month": month,
                "payment": round(monthly_payment, 2),
                "balance": max(round(balance, 2), 0),
            }
        )

    return render(
        request,
        "payroll/admin/loan_schedule.html",
        {
            "loan": loan,
            "schedule": schedule,
            "total_payable": round(total_payable, 2),
        },
    )


