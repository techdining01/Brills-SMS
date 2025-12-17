from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()

class Command(BaseCommand):
    help = "Seed users (admin, teacher, parent, student)"

    def handle(self, *args, **kwargs):
        roles = {
            "admin": 2,
            "teacher": 5,
            "parent": 5,
            "student": 10,
        }

        created = 0

        for role, count in roles.items():
            for i in range(count):
                email = f"{role}{i+1}@brillsschool.com"
                username = f"{role}{i+1}"

                if User.objects.filter(email=email).exists():
                    continue

                User.objects.create_user(
                    email=email,
                    password="password123",
                    first_name=role.capitalize(),
                    last_name=f"User{i+1}",
                    role=role,
                    is_approved=True,   
                    username = f"user_{uuid.uuid4().hex[:10]}"
                )

                created += 1

        self.stdout.write(
            self.style.SUCCESS(f"✅ Seeded {created} users safely")
        )
