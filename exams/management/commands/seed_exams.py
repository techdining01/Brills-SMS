from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import User
from exams.models import Exam, Question
from exams.models import SchoolClass

class Command(BaseCommand):
    help = "Seed exams, classes, questions"

    def handle(self, *args, **kwargs):
        staff = User.objects.filter(role=User.Role.STAFF).first()
        students = User.objects.filter(role=User.Role.STUDENT)

        school_class, _ = SchoolClass.objects.get_or_create(
            name="Primary 5",
            arm="A"
        )

        exam = Exam.objects.create(
            title="Mid Term Exam",
            school_class=school_class,
            created_by=staff,
            duration=60,
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(days=1),
            is_active=True,
            is_published=True
        )

        for i in range(10):
            Question.objects.create(
                exam=exam,
                text=f"What is question {i+1}?",
                type="objective",
                marks=2
            )

        self.stdout.write(self.style.SUCCESS("Exams seeded successfully"))
