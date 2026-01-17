from django.core.management.base import BaseCommand
from decimal import Decimal
from django.contrib.auth import get_user_model
from payroll.models import PayrollPeriod, StaffProfile, Payee
from payroll.services.payroll_generation import bulk_generate_payroll
from loans.models import LoanApplication



class Command(BaseCommand):
    help = "Seed payroll, staff, loans for testing"

    def handle(self, *args, **kwargs):
        User = get_user_model()



        admin = User.objects.filter(role="ADMIN").first()
        payee = Payee.objects.get(user=admin)
        staff = StaffProfile.objects.get(payee=payee)
        if not staff:
            self.stdout.write(self.style.ERROR("Admin user required"))
            return

        period, _ = PayrollPeriod.objects.get_or_create(
            month=9,
            year=2025
        )

        # Staff
        staff, _ = StaffProfile.objects.get_or_create(
            user=staff,
            defaults={
                "monthly_salary": Decimal("200000"),
                "is_active": True,
            }
        )

        # LoanApplication
        LoanApplication.objects.get_or_create(
            payee=staff,
            defaults={
                "amount": Decimal("500000"),
                "monthly_deduction": Decimal("50000"),
                "outstanding_balance": Decimal("500000"),
                "status": "approved",
            }
        )

        result = bulk_generate_payroll(
            payroll_period=period,
            generated_by=staff
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded payroll. Created: {result['created']}, Skipped: {result['skipped']}"
            )
        )
