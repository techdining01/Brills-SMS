from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import date

from payroll.models import (
    Payee, BankAccount,
    SalaryComponent, SalaryStructure, SalaryStructureItem,
    PayeeSalaryStructure,
    PayrollPeriod, PayrollRecord,
    PayrollLineItem, PayslipItem,
    StaffProfile,
    LeaveType, LeaveRequest
)

User = get_user_model()


class Command(BaseCommand):
    help = "Seed payroll and leave using canonical models only"

    def handle(self, *args, **kwargs):
        admin, _ = User.objects.get_or_create(
            username="admin",
            defaults={"is_staff": True, "is_superuser": True}
        )

        # -------------------------------------------------
        # USERS / PAYEES / STAFF
        # -------------------------------------------------
        payees = []
        for i in range(1, 6):
            user, _ = User.objects.get_or_create(
                username=f"staff{i}",
                defaults={"is_staff": False}
            )

            payee, _ = Payee.objects.get_or_create(
                reference_code=f"PAYEE{i:03}",
                defaults={
                    "user": user,
                    "full_name": f"Staff Member {i}",
                    "payee_type": "teacher" if i <= 3 else "non_teacher",
                }
            )
            payees.append(payee)

            StaffProfile.objects.get_or_create(
                payee=payee,
                defaults={
                    "phone_number": f"080000000{i}",
                    "address": "Test Address",
                    "date_of_employment": date(2022, 1, 1),
                    "is_confirmed": True,
                }
            )

            BankAccount.objects.get_or_create(
                payee=payee,
                account_number=f"01234567{i}",
                defaults={
                    "bank_name": "Access Bank",
                    "account_name": payee.full_name,
                    "is_primary": True,
                }
            )

        # -------------------------------------------------
        # SALARY COMPONENTS
        # -------------------------------------------------
        components = {
            "Basic Salary": ("earning", False),
            "Tax": ("deduction", True),
            "Pension": ("deduction", False),
            "Bonus": ("earning", False),
        }

        component_objs = {}
        for name, (ctype, taxable) in components.items():
            component_objs[name], _ = SalaryComponent.objects.get_or_create(
                name=name,
                defaults={
                    "component_type": ctype,
                    "is_taxable": taxable,
                }
            )

        # -------------------------------------------------
        # SALARY STRUCTURE
        # -------------------------------------------------
        structure, _ = SalaryStructure.objects.get_or_create(
            name="Teacher Default Structure",
            payee_type="teacher",
            defaults={"created_by": admin},
        )

        SalaryStructureItem.objects.get_or_create(
            salary_structure=structure,
            component=component_objs["Basic Salary"],
            defaults={"amount": Decimal("120000")},
        )

        SalaryStructureItem.objects.get_or_create(
            salary_structure=structure,
            component=component_objs["Tax"],
            defaults={"percentage": Decimal("10")},
        )

        SalaryStructureItem.objects.get_or_create(
            salary_structure=structure,
            component=component_objs["Pension"],
            defaults={"percentage": Decimal("8")},
        )

        for payee in payees:
            PayeeSalaryStructure.objects.get_or_create(
                payee=payee,
                defaults={
                    "salary_structure": structure,
                    "assigned_by": admin,
                }
            )

        # -------------------------------------------------
        # PAYROLL PERIOD
        # -------------------------------------------------
        period, _ = PayrollPeriod.objects.get_or_create(
            month=8,
            year=2025,
        )

        # -------------------------------------------------
        # PAYROLL RECORDS + LINE ITEMS
        # -------------------------------------------------
        for payee in payees:
            gross = Decimal("120000")
            tax = gross * Decimal("0.10")
            pension = gross * Decimal("0.08")
            deductions = tax + pension
            net = gross - deductions

            record, _ = PayrollRecord.objects.get_or_create(
                payee=payee,
                payroll_period=period,
                defaults={
                    "gross_pay": gross,
                    "total_deductions": deductions,
                    "net_pay": net,
                    "generated_by": admin,
                }
            )

            PayrollLineItem.objects.get_or_create(
                payroll_record=record,
                component=component_objs["Basic Salary"],
                line_type="earning",
                amount=gross,
            )

            PayrollLineItem.objects.get_or_create(
                payroll_record=record,
                component=component_objs["Tax"],
                line_type="deduction",
                amount=tax,
            )

            PayrollLineItem.objects.get_or_create(
                payroll_record=record,
                component=component_objs["Pension"],
                line_type="deduction",
                amount=pension,
            )

            PayslipItem.objects.get_or_create(
                payroll_record=record,
                component_name="Basic Salary",
                component_type="earning",
                calculation_type="fixed",
                value=gross,
            )

        # -------------------------------------------------
        # LEAVE TYPES & REQUESTS
        # -------------------------------------------------
        annual, _ = LeaveType.objects.get_or_create(
            name="Annual Leave",
            defaults={"is_paid": True, "default_days": 14},
        )

        unpaid, _ = LeaveType.objects.get_or_create(
            name="Unpaid Leave",
            defaults={"is_paid": False, "default_days": 0},
        )

        for payee in payees:
            staff = payee.staffprofile

            LeaveRequest.objects.get_or_create(
                staff=staff,
                leave_type=unpaid,
                start_date=date(2025, 8, 10),
                end_date=date(2025, 8, 12),
                defaults={
                    "reason": "Personal",
                    "status": "approved",
                    "approved_by": admin,
                }
            )

        self.stdout.write(self.style.SUCCESS("✅ Payroll + Leave seeded correctly"))
