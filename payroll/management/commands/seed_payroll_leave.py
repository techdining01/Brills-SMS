from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
import random

from payroll.models import (
    Payee,
    BankAccount,
    SalaryComponent,
    SalaryStructure,
    SalaryStructureItem,
    PayeeSalaryStructure,
    PayrollPeriod,
    PayrollRecord,
    PayrollAuditLog,
    StaffProfile,
)

User = get_user_model()


class Command(BaseCommand):
    help = "Seed payroll system with realistic data"

    def handle(self, *args, **kwargs):
        self.stdout.write("🚀 Seeding payroll system...")

        # 1️⃣ USERS
        admin, _ = User.objects.get_or_create(
            username="admin",
            defaults={"is_staff": True, "is_superuser": True},
        )
        admin.set_password("admin123")
        admin.save()

        # 2️⃣ PAYEES
        payees = []
        for i in range(5):
            payee = Payee.objects.create(
                full_name=f"Staff {i+1}",
                payee_type="teacher",
                reference_code=f"STF-{i+1:03}",
            )
            payees.append(payee)

        # 3️⃣ BANK ACCOUNTS
        for payee in payees:
            BankAccount.objects.create(
                payee=payee,
                bank_name="GTBank",
                account_number=f"01234567{random.randint(10,99)}",
                account_name=payee.full_name,
                is_primary=True,
            )

        # 4️⃣ STAFF PROFILES
        for payee in payees:
            StaffProfile.objects.create(
                payee=payee,
                phone_number="08012345678",
                address="School Quarters",
                date_of_employment=timezone.now().date(),
                is_confirmed=True,
            )

        # 5️⃣ SALARY COMPONENTS
        basic = SalaryComponent.objects.create(
            name="Basic Salary", component_type="earning"
        )
        housing = SalaryComponent.objects.create(
            name="Housing Allowance", component_type="earning"
        )
        tax = SalaryComponent.objects.create(
            name="PAYE Tax", component_type="deduction", is_taxable=True
        )

        # 6️⃣ SALARY STRUCTURE
        structure = SalaryStructure.objects.create(
            name="Teacher Standard",
            payee_type="teacher",
            created_by=admin,
        )

        # 7️⃣ STRUCTURE ITEMS
        SalaryStructureItem.objects.create(
            salary_structure=structure,
            component=basic,
            amount=Decimal("120000"),
        )
        SalaryStructureItem.objects.create(
            salary_structure=structure,
            component=housing,
            amount=Decimal("30000"),
        )
        SalaryStructureItem.objects.create(
            salary_structure=structure,
            component=tax,
            percentage=Decimal("10.00"),
        )

        # 8️⃣ ASSIGN STRUCTURE
        for payee in payees:
            PayeeSalaryStructure.objects.create(
                payee=payee,
                salary_structure=structure,
                assigned_by=admin,
            )

        # 9️⃣ PAYROLL PERIOD
        period = PayrollPeriod.objects.create(
            month=1,
            year=2025,
            status="draft",
        )

        # 🔟 PAYROLL RECORDS
        for payee in payees:
            gross = Decimal("150000")
            deductions = Decimal("15000")
            net = gross - deductions

            PayrollRecord.objects.create(
                payee=payee,
                payroll_period=period,
                gross_pay=gross,
                total_deductions=deductions,
                net_pay=net,
                generated_by=admin,
                status="pending",
            )

        # 1️⃣1️⃣ AUDIT LOG
        PayrollAuditLog.objects.create(
            action="Seeded payroll system",
            performed_by=admin,
            metadata={"period": str(period)},
        )

        self.stdout.write(self.style.SUCCESS("✅ Payroll seeding completed successfully"))
