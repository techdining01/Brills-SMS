from django.core.management.base import BaseCommand
from ...models import LeaveType

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        leaves = [
            ("Annual Leave", 21),
            ("Sick Leave", 10),
            ("Maternity Leave", 90),
            ("Paternity Leave", 14),
            ("Unpaid Leave", 0),
        ]

        for name, annual_days in leaves:
            LeaveType.objects.get_or_create(
                name=name,
                defaults={
    
                    "annual_days": annual_days
                }
            )

        self.stdout.write(self.style.SUCCESS("Leave types seeded"))
