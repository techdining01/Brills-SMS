# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.decorators import login_required, user_passes_test
# from django.contrib import messages
# from .models import Loan, LoanRepayment, LoanSchedule
# from decimal import Decimal
# from payroll.models import PayrollLineItem, SalaryComponent, PayrollRecord, PayrollPeriod, PaymentBatch
# from leaves.models import LeaveRequest
# from django.http import HttpResponse
# from django.contrib.admin.views.decorators import staff_member_required
# from django.utils import timezone
# from payroll.models import AuditLog
# from django.conf import settings


# @login_required
# def request_loan(request):
#     payee = request.user.payee

#     if request.method == "POST":
#         principal = Decimal(request.POST["amount"])
#         months = int(request.POST["months"])
#         monthly = principal / months

#         Loan.objects.create(
#             payee=payee,
#             principal=principal,
#             months=months,
#             monthly_deduction=monthly
#         )
#         messages.success(request, "Loan request submitted.")
#         return redirect("staff:loan_dashboard")

#     return render(request, "staff/loan_request.html")


# @login_required
# @user_passes_test(lambda u: u.role == "ADMIN")
# def approve_loan(request, loan_id):
#     loan = get_object_or_404(Loan, id=loan_id, status="pending")
#     loan.status = "approved"
#     loan.approved_by = request.user
#     loan.save()
#     messages.success(request, "Loan approved.")
#     return redirect("admin_loan_list")



# def apply_loans(payee, payroll_record):
#     loans = Loan.objects.filter(payee=payee, status="approved")

#     for loan in loans:
#         LoanRepayment.objects.create(
#             loan=loan,
#             payroll_record=payroll_record,
#             amount=loan.monthly_deduction
#         )

#         PayrollLineItem.objects.create(
#             payroll_record=payroll_record,
#             component=SalaryComponent.objects.get(name="Loan Deduction"),
#             line_type="deduction",
#             amount=loan.monthly_deduction,
#             metadata={"loan_id": loan.id}
#         )




# @login_required
# def staff_loan_payroll_dashboard(request):
#     payee = request.user.payee

#     return render(request, "loans/staff/dashboard.html", {
#         "payslips": PayrollRecord.objects.filter(payee=payee),
#         "loans": Loan.objects.filter(payee=payee).prefetch_related("repayments"),
#         "leaves": LeaveRequest.objects.filter(staff__payee=payee),
#     })


# @login_required
# @user_passes_test(lambda u: u.role == "ADMIN")
# def admin_loan_payroll_dashboard(request):
#     return render(request, "loans/admin/loan_payroll_dashboard.html", {
#         "periods": PayrollPeriod.objects.all(),
#         "pending_loans": Loan.objects.filter(status="pending"),
#         "batches": PaymentBatch.objects.all(),
#     })



# def apply_loan_deduction(payee, payroll):
#     schedules = LoanSchedule.objects.filter(
#         loan__payee=payee,
#         paid=False
#     ).order_by("month")

#     if schedules.exists():
#         schedule = schedules.first()
#         payroll.add_deduction(
#             "Loan Repayment",
#             schedule.total_payment
#         )
#         schedule.paid = True
#         schedule.save()



# @staff_member_required
# def admin_loans_list(request):
#     loans = Loan.objects.select_related("payee").order_by("-requested_at")

#     status = request.GET.get("status")
#     if status:
#         loans = loans.filter(status=status)

#     return render(
#         request,
#         "payroll/admin/loan_list.html",
#         {
#             "loans": loans,
#             "status": status,
#         },
#     )


# @staff_member_required
# def approve_loan(request, loan_id):
#     loan = get_object_or_404(Loan, id=loan_id)

#     if loan.status != "pending":
#         return redirect("admin_loans")

#     loan.status = "approved"
#     loan.approved_by = request.user
#     loan.approved_at = timezone.now()
#     loan.save()

#     AuditLog.objects.create(
#         user=request.user,
#         action="APPROVE",
#         object_type="Loan",
#         object_id=str(loan.id),
#         description=f"Approved loan for {loan.payee.full_name}",
#     )

#     return redirect("admin_loans")



# @staff_member_required
# def reject_loan(request, loan_id):
#     loan = get_object_or_404(Loan, id=loan_id)

#     if loan.status != "pending":
#         return redirect("admin_loans")

#     loan.status = "rejected"
#     loan.save()

#     AuditLog.objects.create(
#         user=request.user,
#         action="FAIL",
#         object_type="Loan",
#         object_id=str(loan.id),
#         description=f"Rejected loan for {loan.payee.full_name}",
#     )

#     return redirect("admin_loans")


# @staff_member_required
# def loan_amortization_table(request, loan_id):
#     loan = get_object_or_404(Loan, id=loan_id)

#     total_interest = (
#         loan.amount * loan.interest_rate / Decimal("100")
#     )
#     total_payable = loan.amount + total_interest
#     monthly_payment = total_payable / loan.duration_months

#     schedule = []
#     balance = total_payable

#     for month in range(1, loan.duration_months + 1):
#         balance -= monthly_payment
#         schedule.append(
#             {
#                 "month": month,
#                 "payment": round(monthly_payment, 2),
#                 "balance": max(round(balance, 2), 0),
#             }
#         )

#     return render(
#         request,
#         "payroll/admin/loan_schedule.html",
#         {
#             "loan": loan,
#             "schedule": schedule,
#             "total_payable": round(total_payable, 2),
#         },
#     )




# loans/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import LoanApplication, LoanRepayment
from payroll.models import PayrollRecord

from django.core.paginator import Paginator
from django.db.models import Sum
from django.http import JsonResponse

@login_required
def admin_loan_list(request):
    if request.user.role not in ["ADMIN", "BURSAR"]:
        messages.error(request, "Permission denied.")
        return redirect("payroll:dashboard")

    loans_qs = LoanApplication.objects.order_by("-applied_at")
    
    # Pagination
    paginator = Paginator(loans_qs, 10)  # 10 loans per page
    page_number = request.GET.get("page")
    loans = paginator.get_page(page_number)

    # Chart Data
    total_principal = loans_qs.aggregate(Sum('principal_amount'))['principal_amount__sum'] or 0
    total_outstanding = loans_qs.aggregate(Sum('outstanding_balance'))['outstanding_balance__sum'] or 0
    total_approved = loans_qs.filter(status="approved").count()
    total_pending = loans_qs.filter(status="pending").count()

    context = {
        "loans": loans,
        "total_principal": total_principal,
        "total_outstanding": total_outstanding,
        "total_approved": total_approved,
        "total_pending": total_pending,
    }

    return render(request, "loans/admin_loan_list.html", context)


# AJAX endpoint for chart (optional)
@login_required
def admin_loan_chart_data(request):
    if request.user.role not in ["ADMIN", "BURSAR"]:
        return JsonResponse({"error": "Permission denied."}, status=403)

    data = LoanApplication.objects.values('status').annotate(total=Sum('principal_amount'))
    chart_data = {
        "labels": [d['status'].capitalize() for d in data],
        "data": [float(d['total']) for d in data],
    }
    return JsonResponse(chart_data)


@login_required
def admin_loan_detail(request, loan_id):
    loan = get_object_or_404(LoanApplication, id=loan_id)
    repayments = loan.repayments.order_by("-created_at")
    return render(request, "loans/admin_loan_detail.html", {"loan": loan, "repayments": repayments})

@login_required
def approve_loan(request, loan_id):
    loan = get_object_or_404(LoanApplication, id=loan_id)
    if request.user.role not in ["ADMIN", "BURSAR"]:
        messages.error(request, "Permission denied.")
        return redirect("loans:admin_loan_detail", loan.id)
    
    try:
        loan.approve(request.user)
        messages.success(request, "Loan approved successfully.")
    except Exception as e:
        messages.error(request, str(e))
    
    return redirect("loans:admin_loan_detail", loan.id)

@login_required
def reject_loan(request, loan_id):
    loan = get_object_or_404(LoanApplication, id=loan_id)
    if request.user.role not in ["ADMIN", "BURSAR"]:
        messages.error(request, "Permission denied.")
        return redirect("loans:admin_loan_detail", loan.id)
    
    try:
        loan.reject(request.user)
        messages.success(request, "Loan rejected successfully.")
    except Exception as e:
        messages.error(request, str(e))
    
    return redirect("loans:admin_loan_detail", loan.id)


from django.core.paginator import Paginator

@login_required
def staff_loan_dashboard(request):
    payee = Payee.objects.get(user=request.user)
    loans_qs = payee.loans.order_by("-applied_at")

    paginator = Paginator(loans_qs, 5)  # 5 loans per page
    page_number = request.GET.get("page")
    loans = paginator.get_page(page_number)

    # Calculate progress percentage
    for loan in loans:
        loan.progress = 0
        if loan.total_amount > 0:
            loan.progress = int((loan.total_amount - loan.outstanding_balance) / loan.total_amount * 100)

    return render(request, "loans/staff_loan_dashboard.html", {"loans": loans})
