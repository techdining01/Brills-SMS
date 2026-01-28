from decimal import Decimal
from payroll.models import (
    SalaryStructureItem,
    PayrollRecord,
    PayrollAuditLog,
    PayslipItem,
    PayeeSalaryStructure,
)

class PayrollCalculationError(Exception):
    pass



def calculate_payroll(*, payee, payroll_period, generated_by):
    if payroll_period.status != "draft":
        raise PayrollCalculationError("Payroll period must be draft.")

    try:
        assignment = payee.salary_assignment
    except PayeeSalaryStructure.DoesNotExist:
        raise PayrollCalculationError("Payee has no salary structure assigned.")

    structure = assignment.salary_structure

    items = SalaryStructureItem.objects.select_related(
        "component"
    ).filter(salary_structure=structure)

    if not items.exists():
        raise PayrollCalculationError("Salary structure has no components.")

    earnings = Decimal("0.00")
    deductions = Decimal("0.00")
    breakdown = []

    # Fixed amounts
    for item in items:
        if item.amount:
            value = item.amount
            comp = item.component

            if comp.component_type == "earning":
                earnings += value
            else:
                deductions += value

            breakdown.append({
                "name": comp.name,
                "type": comp.component_type,
                "calc": "fixed",
                "value": value,
            })

    # Percentage amounts (based on earnings)
    for item in items:
        if item.percentage:
            comp = item.component
            value = (earnings * item.percentage) / Decimal("100")

            if comp.component_type == "earning":
                earnings += value
            else:
                deductions += value

            breakdown.append({
                "name": comp.name,
                "type": comp.component_type,
                "calc": "percentage",
                "value": value,
            })

    net_pay = earnings - deductions

    if net_pay < 0:
        raise PayrollCalculationError("Net pay cannot be negative.")

    payroll_record = PayrollRecord.objects.create(
        payee=payee,
        payroll_period=payroll_period,
        gross_pay=earnings,
        total_deductions=deductions,
        net_pay=net_pay,
        generated_by=generated_by,
    )

    for item in breakdown:
        PayslipItem.objects.create(
            payroll_record=payroll_record,
            component_name=item["name"],
            component_type=item["type"],
            calculation_type=item["calc"],
            value=item["value"],
        )

    PayrollAuditLog.objects.create(
        action="Payroll Generated",
        performed_by=generated_by,
        metadata={
            "payee": payee.full_name,
            "period": str(payroll_period),
            "net_pay": str(net_pay),
        },
    )

    return payroll_record


