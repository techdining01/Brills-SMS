from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import LoanApplication, LoanRepayment
from payroll.models import Payee
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



@login_required
def staff_loan_dashboard(request):
    payee = Payee.objects.get(user=request.user)
    loans_qs = payee.loans.order_by("-applied_at")

    paginator = Paginator(loans_qs, 5) 
    page_number = request.GET.get("page")
    loans = paginator.get_page(page_number)

    # Calculate progress percentage
    for loan in loans:
        loan.progress = 0
        if loan.total_amount > 0:
            loan.progress = int((loan.total_amount - loan.outstanding_balance) / loan.total_amount * 100)

    return render(request, "loans/staff/loan_dashboard.html", {"loans": loans})
