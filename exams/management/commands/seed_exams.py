from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from exams.models import (
    SchoolClass, Subject, Exam, Question, Choice,
    ExamAccess, ExamAttempt, StudentAnswer, SubjectiveMark
)
from accounts.models import Student
import random

User = get_user_model()


class Command(BaseCommand):
    help = "Seed full examination system (classes, exams, questions, attempts, grading)"

    def handle(self, *args, **kwargs):

        self.stdout.write("⏳ Seeding examination system...")

        # ------------------------------------------------
        # 1. CLASSES
        # ------------------------------------------------
        classes = []
        for name in ["JSS1", "JSS2", "SSS1"]:
            cls, _ = SchoolClass.objects.get_or_create(
                name=name,
                defaults={"level": "junior_secondary"}
            )
            classes.append(cls)

        # ------------------------------------------------
        # 2. TEACHER / ADMIN
        # ------------------------------------------------
        teacher = User.objects.filter(role="TEACHER").first()
        admin = User.objects.filter(is_superuser=True).first()

        examiner = teacher or admin
        if not examiner:
            self.stdout.write(self.style.ERROR("❌ No teacher/admin found"))
            return

        # ------------------------------------------------
        # 3. SUBJECTS
        # ------------------------------------------------
        subject = Subject.objects.filter(
            name="Mathematics"
        ).first()

        if not subject:
            subject = Subject.objects.create(
                name="Mathematics",
                created_by=examiner
            )

        subject.classes.add(cls)

        # ------------------------------------------------
        # 4. STUDENTS
        # ------------------------------------------------
        students = Student.objects.all()

        if not students.exists():
            self.stdout.write(self.style.ERROR("❌ No students found"))
            return

        # ------------------------------------------------
        # 5. EXAMS
        # ------------------------------------------------
        exams = []
        for cls in classes:
            exam, _ = Exam.objects.get_or_create(
                title=f"{cls.name} Mathematics Test",
                school_class=cls,
                created_by=examiner,
                defaults={
                    "duration": 30,
                    "start_time": timezone.now(),
                    "end_time": timezone.now() + timezone.timedelta(days=7),
                    "is_active": True,
                    "is_published": True,
                    "allow_retake": True
                }
            )
            exams.append(exam)

        # ------------------------------------------------
        # 6. QUESTIONS
        # ------------------------------------------------
        for exam in exams:
            questions = []

            # Objective
            for i in range(5):
                q = Question.objects.create(
                    exam=exam,
                    text=f"Objective Question {i+1}",
                    type="objective",
                    marks=2
                )
                correct = random.randint(1, 4)

                for j in range(1, 5):
                    Choice.objects.create(
                        question=q,
                        text=f"Option {j}",
                        is_correct=(j == correct)
                    )

                questions.append(q)

            # Subjective
            for i in range(2):
                q = Question.objects.create(
                    exam=exam,
                    text=f"Subjective Question {i+1}",
                    type="subjective",
                    marks=10
                )
                questions.append(q)

        # ------------------------------------------------
        # 7. EXAM ACCESS
        # ------------------------------------------------
        for exam in exams:
            for student in students.filter(student_class=exam.school_class):
                ExamAccess.objects.get_or_create(
                    student=student,
                    exam=exam,
                    defaults={"via_payment": True}
                )

        # ------------------------------------------------
        # 8. ATTEMPTS + ANSWERS + GRADING
        # ------------------------------------------------
        for exam in exams:
            exam_questions = list(exam.question_set.all())

            for student in students.filter(student_class=exam.school_class):
                random.shuffle(exam_questions)

                attempt = ExamAttempt.objects.create(
                    student=student,
                    exam=exam,
                    status="submitted",
                    is_submitted=True,
                    score=0,
                    question_order=[q.id for q in exam_questions],
                    completed_at=timezone.now()
                )

                objective_score = 0

                for q in exam_questions:
                    if q.type == "objective":
                        correct_choice = q.choice_set.filter(is_correct=True).first()
                        chosen = random.choice(list(q.choice_set.all()))

                        StudentAnswer.objects.create(
                            attempt=attempt,
                            question=q,
                            selected_choice=chosen
                        )

                        if chosen == correct_choice:
                            objective_score += q.marks

                    else:
                        ans = StudentAnswer.objects.create(
                            attempt=attempt,
                            question=q,
                            answer_text="Sample subjective answer"
                        )

                        SubjectiveMark.objects.create(
                            answer=ans,
                            score=random.randint(4, q.marks),
                            marked_by=exam.created_by
                        )

                attempt.score = objective_score
                attempt.save(update_fields=["score"])

        self.stdout.write(self.style.SUCCESS("✅ Full examination system seeded successfully"))
