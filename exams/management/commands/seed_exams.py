from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from exams.models import Exam, Question, Choice, SchoolClass, Subject


User = get_user_model()


class Command(BaseCommand):
    help = "Seed realistic classes, subjects, exams and questions"

    def handle(self, *args, **options):
        if Exam.objects.exists():
            self.stdout.write(self.style.WARNING("Exams already exist, skipping exam seeding"))
            return

        teacher = (
            User.objects.filter(role=getattr(User.Role, "TEACHER", "TEACHER")).first()
            or User.objects.filter(is_staff=True).first()
        )
        if not teacher:
            self.stderr.write("❌ No teacher or staff user found. Run seed_accounts first.")
            return

        current_year = timezone.now().year
        academic_year = f"{current_year}/{current_year + 1}"

        class_specs = [
            ("JSS1", "junior_secondary"),
            ("JSS2", "junior_secondary"),
            ("JSS3", "junior_secondary"),
        ]

        classes = []
        for name, level in class_specs:
            cls, _ = SchoolClass.objects.get_or_create(
                name=name,
                defaults={
                    "level": level,
                    "academic_year": academic_year,
                    "description": f"{name} {academic_year}",
                    "teacher": teacher,
                },
            )
            classes.append(cls)

        subject_names = ["Mathematics", "English Language", "Basic Science"]
        subjects = []
        for name in subject_names:
            subject, _ = Subject.objects.get_or_create(
                name=name,
                defaults={
                    "description": f"{name} seeded subject",
                    "department": "Academics",
                    "created_by": teacher,
                },
            )
            if not subject.classes.exists():
                subject.classes.set(classes)
            subjects.append(subject)

        now = timezone.now()
        exams_created = 0

        for cls in classes:
            for subject in subjects:
                title = f"{cls.name} {subject.name} Term Test"

                exam, created = Exam.objects.get_or_create(
                    title=title,
                    school_class=cls,
                    defaults={
                        "created_by": teacher,
                        "duration": 40,
                        "start_time": now + timedelta(days=1),
                        "end_time": now + timedelta(days=1, minutes=40),
                        "is_active": True,
                        "is_published": True,
                        "allow_retake": False,
                        "requires_payment": False,
                        "price": 0,
                        "passing_marks": 40,
                    },
                )

                if not created:
                    continue

                exams_created += 1

                if subject.name == "Mathematics":
                    questions_data = [
                        {
                            "text": "What is 7 × 6?",
                            "options": ["11", "36", "42", "56"],
                            "correct_index": 3,
                        },
                        {
                            "text": "What is 3/5 as a percentage?",
                            "options": ["20%", "40%", "60%", "80%"],
                            "correct_index": 3,
                        },
                        {
                            "text": "What is the next number in the sequence 2, 4, 8, 16, ?",
                            "options": ["18", "24", "30", "32"],
                            "correct_index": 4,
                        },
                    ]
                elif subject.name == "English Language":
                    questions_data = [
                        {
                            "text": "Choose the correct sentence.",
                            "options": [
                                "She do her homework every day.",
                                "She does her homework every day.",
                                "She dids her homework every day.",
                                "She did her homework every days.",
                            ],
                            "correct_index": 2,
                        },
                        {
                            "text": "Which word is a noun?",
                            "options": ["quickly", "beautiful", "teacher", "slowly"],
                            "correct_index": 3,
                        },
                        {
                            "text": "Which of these is a correct question tag: \"You are coming, ___?\"",
                            "options": ["isn't you", "are you", "aren't you", "do you"],
                            "correct_index": 3,
                        },
                    ]
                else:
                    questions_data = [
                        {
                            "text": "Which gas do humans need to breathe in to stay alive?",
                            "options": ["Carbon dioxide", "Oxygen", "Nitrogen", "Helium"],
                            "correct_index": 2,
                        },
                        {
                            "text": "What is the main source of energy for the Earth?",
                            "options": ["The Moon", "The Sun", "The oceans", "The wind"],
                            "correct_index": 2,
                        },
                        {
                            "text": "Water changes to ice at what temperature?",
                            "options": ["0°C", "10°C", "50°C", "100°C"],
                            "correct_index": 1,
                        },
                    ]

                for index, q in enumerate(questions_data, start=1):
                    question = Question.objects.create(
                        exam=exam,
                        text=q["text"],
                        type="objective",
                        marks=1,
                        order=index,
                    )

                    for idx, option_text in enumerate(q["options"], start=1):
                        Choice.objects.create(
                            question=question,
                            text=option_text,
                            is_correct=idx == q["correct_index"],
                        )

        self.stdout.write(
            self.style.SUCCESS(f"✅ Exam seeding completed. Exams created: {exams_created}")
        )
