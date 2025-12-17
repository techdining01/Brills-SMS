import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model

from pickup.models import (
    PickupAuthorization,
    PickupStudent,
    PickupVerificationLog
)

User = get_user_model()


class Command(BaseCommand):
    help = "Seed pickup authorizations with QR and verification logs"

    def handle(self, *args, **kwargs):
        parents = User.objects.filter(role="PARENT")
        students = User.objects.filter(role="STUDENT")

        if not parents.exists() or not students.exists():
            self.stderr.write("❌ Seed parents and students first")
            return

        for parent in parents[:5]:
            pickup = PickupAuthorization.objects.create(
                parent=parent,
                bearer_name=f"Bearer for {parent.first_name}",
                relationship=random.choice(["Father", "Mother", "Uncle"]),
                expires_at=timezone.now() + timedelta(hours=11),
            )

            attached = random.sample(
                list(students),
                min(random.randint(1, 3), students.count())
            )

            for student in attached:
                PickupStudent.objects.create(
                    pickup=pickup,
                    student=student
                )

            # create fake verification logs
            PickupVerificationLog.objects.create(
                pickup=pickup,
                verified_by=None,
                status=random.choice(["SUCCESS", "EXPIRED", "USED"])
            )

        self.stdout.write(self.style.SUCCESS(
            "✅ Pickups + QR codes + logs seeded successfully"
        ))
