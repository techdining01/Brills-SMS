from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from exams.models import SchoolClass
from django.utils.crypto import get_random_string

User = get_user_model()


class Command(BaseCommand):
    help = "Seed admin, teachers, parents, and students"

    def handle(self, *args, **options):

        self.stdout.write(self.style.WARNING("Seeding accounts..."))

        # --------------------------------------------------
        # Ensure classes exist
        # --------------------------------------------------
        classes = []
        for name in ["JSS1", "JSS2", "JSS3", "SS1", "SS2", "SS3"]:
            cls, _ = SchoolClass.objects.get_or_create(name=name)
            classes.append(cls)

        # --------------------------------------------------
        # Admin
        # --------------------------------------------------
        admin, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@school.com",
                "role": User.Role.ADMIN,
                "is_staff": True,
                "is_superuser": True,
                "is_approved": True,
            }
        )
        if created:
            admin.set_password("admin123")
            admin.save()

        # --------------------------------------------------
        # Teachers
        # --------------------------------------------------
        teachers = []
        for i in range(3):
            t, created = User.objects.get_or_create(
                username=f"teacher{i+1}",
                defaults={
                    "email": f"teacher{i+1}@school.com",
                    "role": User.Role.TEACHER,
                    "is_approved": True,
                }
            )
            if created:
                t.set_password("teacher123")
                t.save()
            teachers.append(t)

        # --------------------------------------------------
        # Parents
        # --------------------------------------------------
        parents = []
        for i in range(5):
            p, created = User.objects.get_or_create(
                username=f"parent{i+1}",
                defaults={
                    "email": f"parent{i+1}@mail.com",
                    "role": User.Role.PARENT,
                    "is_approved": True,
                }
            )
            if created:
                p.set_password("parent123")
                p.save()
            parents.append(p)

        # --------------------------------------------------
        # Students
        # --------------------------------------------------
        for i in range(10):
            parent = parents[i % len(parents)]
            school_class = classes[i % len(classes)]

            student, created = User.objects.get_or_create(
                username=f"student{i+1}",
                defaults={
                    "email": f"student{i+1}@school.com",
                    "role": User.Role.STUDENT,
                    "student_class": school_class,
                    "is_approved": True,
                }
            )

            if created:
                student.set_password("student123")
                student.save()
                student.parents.add(parent)

        self.stdout.write(self.style.SUCCESS("✅ Account seeding completed successfully"))
