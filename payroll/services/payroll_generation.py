from decimal import Decimal
from django.db import transaction
from django.shortcuts import redirect
from  ..models import AuditLog
from loans.models import LoanRepayment, LoanApplication
from payroll.models import PayrollRecord, Payee, PayrollGenerationLog, PayrollLineItem


def bulk_generate_payroll(payroll_period, generated_by):
    if payroll_period.is_locked:
        raise ValueError("Payroll period is locked")

    payees = Payee.objects.filter(is_active=True)

    results = {
        "success": 0,
        "failed": 0,
    }

    for payee in payees:
        # Skip if already generated
        if PayrollRecord.objects.filter(
            payee=payee,
            payroll_period=payroll_period
        ).exists():
            continue

        try:
            generate_payroll_for_payee(
                payee=payee,
                payroll_period=payroll_period,
                generated_by=generated_by
            )

            PayrollGenerationLog.objects.create(
                payroll_period=payroll_period,
                payee=payee,
                status="success"
            )

            results["success"] += 1

        except Exception as e:
            PayrollGenerationLog.objects.create(
                payroll_period=payroll_period,
                payee=payee,
                status="failed",
                error_message=str(e)
            )

            results["failed"] += 1

            # IMPORTANT: continue processing others
            continue

    payroll_period.is_generated = True
    payroll_period.save()

    return results



@transaction.atomic
def generate_payroll_for_payee(payee, payroll_period, generated_by):
    salary_assignment = payee.salary_assignment
    structure = salary_assignment.salary_structure

    gross = Decimal("0")
    deductions = Decimal("0")

    payroll = PayrollRecord.objects.create(
        payee=payee,
        payroll_period=payroll_period,
        gross_pay=0,
        total_deductions=0,
        net_pay=0,
        generated_by=generated_by,
    )

    # ===============================
    # SALARY COMPONENTS
    # ===============================
    for item in structure.items.select_related("component"):
        if item.amount:
            value = item.amount
        else:
            value = gross * item.percentage / Decimal("100")

        if item.component.component_type == "earning":
            gross += value
        else:
            deductions += value

        PayrollLineItem.objects.create(
            payroll_record=payroll,
            component=item.component,
            line_type=item.component.component_type,
            amount=value,
        )

    # ===============================
    # LOAN DEDUCTION
    # ===============================
    active_loans = LoanApplication.objects.filter(
        payee=payee,
        status="approved",
        outstanding_balance__gt=0,
    )

    for loan in active_loans:
        deduction = min(loan.monthly_deduction, loan.outstanding_balance)
        deductions += deduction

        PayrollLineItem.objects.create(
            payroll_record=payroll,
            component=None,
            line_type="deduction",
            amount=deduction,
            metadata={"type": "loan", "loan_id": loan.id},
        )

        loan.outstanding_balance -= deduction
        LoanRepayment.objects.create(
            loan=loan,
            payroll_record=payroll,
            amount=deduction,
            balance_after=loan.outstanding_balance
        )

        if loan.outstanding_balance <= 0:
            loan.status = "completed"
        loan.save()

    # ===============================
    # FINALIZE PAYROLL
    # ===============================
    payroll.gross_pay = gross
    payroll.total_deductions = deductions
    payroll.net_pay = gross - deductions
    payroll.save()

    AuditLog.objects.create(
        user=generated_by,
        action="CREATE",
        object_type="Payroll",
        object_id=str(payroll.pk),
        description=f"Generated payroll for {payee.full_name}",
    )

    return payroll



