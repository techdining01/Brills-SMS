from django.core.management.base import BaseCommand
from loans.models import LoanApplication
from payroll.models import Payee, PayrollPeriod
from decimal import Decimal

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        period = PayrollPeriod.objects.first()

        for payee in Payee.objects.all()[:5]:
            LoanApplication.objects.get_or_create(
                payee=payee,
                loan_amount=Decimal("50000"),
                defaults={
                    "tenure_months": 5,
                    "loan_type": "personal",
                }
            )
