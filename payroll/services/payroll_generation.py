# payroll/services/payroll_generation.py
from decimal import Decimal
from payroll.models import PayrollRecord, StaffProfile

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
