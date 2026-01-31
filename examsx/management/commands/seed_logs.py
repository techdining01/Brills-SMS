from django.core.management.base import BaseCommand
from exams.models import SystemLog

class Command(BaseCommand):
    help = "Seed system logs"

    def handle(self, *args, **kwargs):
        for i in range(20):
            SystemLog.objects.create(
                level="INFO",
                message=f"Sample log entry {i}"
            )

        self.stdout.write(self.style.SUCCESS("System logs seeded"))
