# payroll/management/commands/seed_payroll.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from payroll.models import (
    Payee, BankAccount, SalaryComponent, SalaryStructure,
    SalaryStructureItem, PayrollPeriod, PayrollRecord,
    PayrollEnrollment, AuditLog, PaymentBatch, PaymentTransaction
)
from decimal import Decimal
import random

User = get_user_model()


class Command(BaseCommand):
    help = "Seed payroll with users, payees, banks, salary structures, payroll periods, records, and transactions."

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding payroll data...")

        # 1️⃣ Create sample users
        roles = ["admin", "teachers", "non_teacher", "contractor", "service_provider"]
        users = []
        for role in roles:
            for i in range(2):  # 2 users per role
                username = f"{role}_{i+1}"
                email = f"{username}@school.com"
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        "email": email,
                        "role": role.upper(),
                        "first_name": f"{role.capitalize()}_{i+1}",
                        "last_name": "Sample",
                    }
                )
                users.append(user)
        self.stdout.write(f"Created {len(users)} sample users.")

        # 2️⃣ Create payees for each user
        payees = []
        for user in users:
            payee, created = Payee.objects.get_or_create(
                user=user,
                defaults={"payee_type": user.role.lower(),
                          "reference_code": f"PAYEE-{random.randint(1000,9999)}",
                          }
            )
            payees.append(payee)

        # 3️⃣ Create primary bank account for each payee
        banks = ["Access Bank", "GTBank", "Zenith Bank", "UBA", "First Bank"]
        for payee in payees:
            BankAccount.objects.get_or_create(
                payee=payee,
                defaults={
                    "bank_name": random.choice(banks),
                    "account_number": f"{random.randint(1000000000, 9999999999)}",
                    "account_name": payee.user.get_full_name(),
                    "is_primary": True
                }
            )

        # 4️⃣ Create salary components
        earnings = ["Basic Salary", "Transport Allowance", "Housing Allowance"]
        deductions = ["Tax", "Pension", "Loan Deduction"]
        components = []

        for name in earnings:
            comp, _ = SalaryComponent.objects.get_or_create(
                name=name,
                component_type="earning"
            )
            components.append(comp)

        for name in deductions:
            comp, _ = SalaryComponent.objects.get_or_create(
                name=name,
                component_type="deduction"
            )
            components.append(comp)

        # 5️⃣ Create salary structure for each payee type
        for payee_type in roles:
            structure, _ = SalaryStructure.objects.get_or_create(
                name=f"{payee_type.capitalize()} Salary Structure",
                payee_type=payee_type,
                created_by=User.objects.filter(role="ADMIN").first()
            )
            # Assign all components with random amounts
            for comp in components:
                SalaryStructureItem.objects.get_or_create(
                    salary_structure=structure,
                    component=comp,
                    amount=Decimal(random.randint(1000, 5000)),
                )

        # 6️⃣ Assign salary structures to payees
        for payee in payees:
            structure = SalaryStructure.objects.filter(payee_type=payee.payee_type).first()
            if structure:
                if not hasattr(payee, "salary_assignment"):
                    from payroll.models import PayeeSalaryStructure
                    PayeeSalaryStructure.objects.create(
                        payee=payee,
                        salary_structure=structure,
                        assigned_by=User.objects.filter(role="ADMIN").first()
                    )

        # 7️⃣ Create payroll periods
        now = timezone.now()
        months = [now.month, now.month - 1 if now.month > 1 else 12]
        for month in months:
            year = now.year if month != 12 else now.year - 1
            PayrollPeriod.objects.get_or_create(month=month, year=year)

        # 8️⃣ Generate payroll records
        for period in PayrollPeriod.objects.all():
            for payee in payees:
                gross = Decimal(random.randint(50000, 150000))
                deductions_total = Decimal(random.randint(5000, 20000))
                net = gross - deductions_total
                PayrollRecord.objects.get_or_create(
                    payee=payee,
                    payroll_period=period,
                    defaults={
                        "gross_pay": gross,
                        "total_deductions": deductions_total,
                        "net_pay": net,
                        "generated_by": User.objects.filter(role="ADMIN").first()
                    }
                )

        # 9️⃣ Mock payment batches and transactions
        for period in PayrollPeriod.objects.all():
            batch, _ = PaymentBatch.objects.get_or_create(
                payroll_period=period,
                created_by=User.objects.filter(role="ADMIN").first()
            )
            for record in PayrollRecord.objects.filter(payroll_period=period):
                PaymentTransaction.objects.get_or_create(
                    payroll_record=record,
                    batch=batch,
                    amount=record.net_pay,
                    bank_name=record.payee.bank_accounts.first().bank_name,
                    account_number=record.payee.bank_accounts.first().account_number,
                    account_name=record.payee.bank_accounts.first().account_name,
                    status="success"
                )

        # 1️⃣0️⃣ Create payroll enrollments
        for user in users:
            payee = Payee.objects.filter(user=user).first()
            if payee:
                from payroll.models import PayrollEnrollment
                PayrollEnrollment.objects.get_or_create(
                    user=user,
                    payee=payee,
                    enrolled_by=User.objects.filter(role="ADMIN").first()
                )

        # 1️⃣1️⃣ Create audit logs
        for payee in payees:
            AuditLog.objects.create(
                user=payee.user,
                action="CREATE",
                object_type="Payee",
                object_id=str(payee.id),
                description=f"Payee {payee} created in seed data."
            )

        self.stdout.write(self.style.SUCCESS("✅ Payroll seed completed successfully!"))
