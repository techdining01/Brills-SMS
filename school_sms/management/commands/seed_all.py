from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = "Seed entire system (accounts, exams, payments, pickups, logs)"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("Seeding Accounts..."))
        call_command("seed_accounts")

        self.stdout.write(self.style.WARNING("Seeding Exams..."))
        call_command("seed_exams")

        self.stdout.write(self.style.WARNING("Seeding BrillsPay..."))
        call_command("seed_brillspay")

        self.stdout.write(self.style.WARNING("Seeding Pickups..."))
        call_command("seed_pickups")

        self.stdout.write(self.style.WARNING("Seeding System Logs..."))
        call_command("seed_logs")

        self.stdout.write(self.style.SUCCESS("✅ ALL DATA SEEDED SUCCESSFULLY"))
