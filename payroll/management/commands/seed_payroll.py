from django.core.management.base import BaseCommand
from payroll.models import SalaryComponent

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        components = [
            ("Basic Salary", "earning"),
            ("Housing Allowance", "earning"),
            ("Loan Deduction", "deduction"),
            ("Tax", "deduction"),
        ]

        for name, ctype in components:
            SalaryComponent.objects.get_or_create(
                name=name,
                defaults={"component_type": ctype}
            )

        self.stdout.write(self.style.SUCCESS("Payroll seeded"))
