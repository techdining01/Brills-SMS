# payroll/management/commands/seed_leave_types.py
from django.core.management.base import BaseCommand
from payroll.models import LeaveType

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        leaves = [
            ("Annual Leave", True, 21),
            ("Sick Leave", True, 10),
            ("Maternity Leave", True, 90),
            ("Paternity Leave", True, 14),
            ("Unpaid Leave", False, 0),
        ]

        for name, is_paid, days in leaves:
            LeaveType.objects.get_or_create(
                name=name,
                defaults={
                    "is_paid": is_paid,
                    "default_days": days
                }
            )

        self.stdout.write(self.style.SUCCESS("Leave types seeded"))
