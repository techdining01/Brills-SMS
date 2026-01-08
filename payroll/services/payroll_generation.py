from decimal import Decimal
from payroll.models import PayrollRecord, StaffProfile, PayrollLineItem
from django.db import transaction
from  ..models import AuditLog
from loans.models import LoanRepayment, Loan



def bulk_generate_payroll(*, payroll_period, generated_by=None):
    """
    Generate payroll records for all active staff for a given period.
    Safe to re-run. Skips existing records.
    """

    if payroll_period.is_locked():
        raise ValueError("Cannot generate payroll for a locked period")

    created = 0
    skipped = 0

    staff_qs = StaffProfile.objects.filter(is_active=True)

    for staff in staff_qs:
        exists = PayrollRecord.objects.filter(
            payee=staff,
            payroll_period=payroll_period
        ).exists()

        if exists:
            skipped += 1
            continue

        gross = staff.monthly_salary
        deductions = Decimal("0.00")   # leave, tax, pension come later
        net = gross - deductions

        PayrollRecord.objects.create(
            payee=staff,
            payroll_period=payroll_period,
            gross_pay=gross,
            total_deductions=deductions,
            net_pay=net,
        )

        created += 1

    return {
        "created": created,
        "skipped": skipped,
        "total_staff": staff_qs.count()
    }




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
    active_loans = Loan.objects.filter(
        payee=payee,
        status="approved",
        outstanding_balance__gt=0,
    )

    for loan in active_loans:
        deduction = min(
            loan.monthly_deduction,
            loan.outstanding_balance
        )

        deductions += deduction

        # Payslip line
        PayrollLineItem.objects.create(
            payroll_record=payroll,
            component=None,
            line_type="deduction",
            amount=deduction,
            metadata={
                "type": "loan",
                "loan_id": loan.id,
            },
        )

        # Loan repayment record
        loan.outstanding_balance -= deduction

        LoanRepayment.objects.create(
            loan=loan,
            payroll_record=payroll,
            amount=deduction,
            balance_after=loan.outstanding_balance,
        )

        # AUTO COMPLETE
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
        object_id=str(payroll.id),
        description=f"Generated payroll for {payee.full_name}",
    )

    return payroll



