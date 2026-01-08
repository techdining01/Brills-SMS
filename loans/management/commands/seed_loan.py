# loans/management/commands/seed_loans.py
from django.core.management.base import BaseCommand
from loans.models import Loan
from payroll.models import Payee, PayrollPeriod
from decimal import Decimal

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        period = PayrollPeriod.objects.first()

        for payee in Payee.objects.all()[:5]:
            Loan.objects.get_or_create(
                payee=payee,
                principal_amount=Decimal("50000"),
                defaults={
                    "interest_rate": 5,
                    "total_payable": Decimal("52500"),
                    "monthly_deduction": Decimal("8750"),
                    "start_period": period,
                }
            )
