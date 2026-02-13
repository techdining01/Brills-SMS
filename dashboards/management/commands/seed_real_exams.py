
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from exams.models import (
    SchoolClass, Subject, Exam, Question, Choice, ExamAttempt, 
    StudentAnswer, SubjectiveMark
)
from dashboards.models import Certificate, ExamAnalytics, StudentPerformance, AttemptHistory
from django.utils import timezone
from datetime import timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Delete existing exam data and seed realistic exam scenarios'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Deleting existing exam data...'))
        
        # Delete dependent data first to avoid integrity errors
        Certificate.objects.all().delete()
        ExamAnalytics.objects.all().delete()
        StudentPerformance.objects.all().delete()
        AttemptHistory.objects.all().delete()
        StudentAnswer.objects.all().delete()
        ExamAttempt.objects.all().delete()
        Choice.objects.all().delete()
        Question.objects.all().delete()
        Exam.objects.all().delete()
        
        self.stdout.write(self.style.SUCCESS('Data deleted successfully.'))
        
        self.stdout.write('Seeding realistic exam data...')
        
        # Ensure we have users and classes
        teacher = User.objects.filter(role='TEACHER').first()
        if not teacher:
            self.stdout.write(self.style.ERROR('No teacher found. Please run populate_demo_data first.'))
            return

        students = User.objects.filter(role='STUDENT')
        if not students.exists():
            self.stdout.write(self.style.ERROR('No students found. Please run populate_demo_data first.'))
            return
            
        school_class = SchoolClass.objects.first()
        if not school_class:
            school_class = SchoolClass.objects.create(name="Grade 10-A", academic_year="2025-2026")

        # ==========================================
        # Exam 1: Computer Science (Objective Only)
        # ==========================================
        cs_exam = Exam.objects.create(
            title="Computer Science Fundamentals",
            school_class=school_class,
            created_by=teacher,
            duration=60,
            start_time=timezone.now() - timedelta(days=5),
            end_time=timezone.now() + timedelta(days=30),
            is_active=True,
            is_published=True,
            passing_marks=50,
            allow_retake=True
        )
        
        cs_questions = [
            {
                "text": "Which of the following is NOT a valid variable name in Python?",
                "type": "objective",
                "marks": 5,
                "choices": [
                    {"text": "my_variable", "is_correct": False},
                    {"text": "_variable", "is_correct": False},
                    {"text": "2variable", "is_correct": True},
                    {"text": "variable2", "is_correct": False}
                ]
            },
            {
                "text": "What is the time complexity of binary search?",
                "type": "objective",
                "marks": 5,
                "choices": [
                    {"text": "O(n)", "is_correct": False},
                    {"text": "O(log n)", "is_correct": True},
                    {"text": "O(n^2)", "is_correct": False},
                    {"text": "O(1)", "is_correct": False}
                ]
            },
            {
                "text": "Which data structure uses LIFO (Last In First Out) principle?",
                "type": "objective",
                "marks": 5,
                "choices": [
                    {"text": "Queue", "is_correct": False},
                    {"text": "Stack", "is_correct": True},
                    {"text": "Tree", "is_correct": False},
                    {"text": "Linked List", "is_correct": False}
                ]
            },
            {
                "text": "What does HTML stand for?",
                "type": "objective",
                "marks": 5,
                "choices": [
                    {"text": "Hyper Text Markup Language", "is_correct": True},
                    {"text": "High Tech Modern Language", "is_correct": False},
                    {"text": "Hyper Transfer Mark Language", "is_correct": False},
                    {"text": "Home Tool Markup Language", "is_correct": False}
                ]
            }
        ]
        
        self.create_questions(cs_exam, cs_questions)

        # ==========================================
        # Exam 2: History (Objective & Theory)
        # ==========================================
        hist_exam = Exam.objects.create(
            title="World History: 20th Century",
            school_class=school_class,
            created_by=teacher,
            duration=90,
            start_time=timezone.now() - timedelta(days=2),
            end_time=timezone.now() + timedelta(days=30),
            is_active=True,
            is_published=True,
            passing_marks=40
        )
        
        hist_questions = [
            {
                "text": "In which year did World War II end?",
                "type": "objective",
                "marks": 2,
                "choices": [
                    {"text": "1943", "is_correct": False},
                    {"text": "1944", "is_correct": False},
                    {"text": "1945", "is_correct": True},
                    {"text": "1946", "is_correct": False}
                ]
            },
            {
                "text": "Who was the first person to walk on the moon?",
                "type": "objective",
                "marks": 2,
                "choices": [
                    {"text": "Yuri Gagarin", "is_correct": False},
                    {"text": "Neil Armstrong", "is_correct": True},
                    {"text": "Buzz Aldrin", "is_correct": False},
                    {"text": "Michael Collins", "is_correct": False}
                ]
            },
            {
                "text": "Analyze the primary causes of the Cold War. Discuss at least two major factors.",
                "type": "subjective",
                "marks": 10,
                "choices": []
            },
            {
                "text": "Describe the impact of the Industrial Revolution on urban life.",
                "type": "subjective",
                "marks": 10,
                "choices": []
            }
        ]
        
        self.create_questions(hist_exam, hist_questions)
        
        # ==========================================
        # Exam 3: Physics (Objective & Theory - Hard)
        # ==========================================
        phy_exam = Exam.objects.create(
            title="Advanced Physics: Mechanics",
            school_class=school_class,
            created_by=teacher,
            duration=120,
            start_time=timezone.now() - timedelta(days=10),
            end_time=timezone.now() + timedelta(days=30),
            is_active=True,
            is_published=True,
            passing_marks=60
        )
        
        phy_questions = [
            {
                "text": "What is the unit of Force in the SI system?",
                "type": "objective",
                "marks": 2,
                "choices": [
                    {"text": "Joule", "is_correct": False},
                    {"text": "Newton", "is_correct": True},
                    {"text": "Watt", "is_correct": False},
                    {"text": "Pascal", "is_correct": False}
                ]
            },
            {
                "text": "According to Newton's Second Law, Force equals:",
                "type": "objective",
                "marks": 2,
                "choices": [
                    {"text": "Mass x Velocity", "is_correct": False},
                    {"text": "Mass x Acceleration", "is_correct": True},
                    {"text": "Mass / Acceleration", "is_correct": False},
                    {"text": "Acceleration / Mass", "is_correct": False}
                ]
            },
            {
                "text": "Explain the concept of Conservation of Energy with a real-world example.",
                "type": "subjective",
                "marks": 15,
                "choices": []
            },
             {
                "text": "Derive the equation for the period of a simple pendulum.",
                "type": "subjective",
                "marks": 15,
                "choices": []
            }
        ]
        
        self.create_questions(phy_exam, phy_questions)

        self.stdout.write(self.style.SUCCESS('Real-world exams created successfully.'))
        
        # ==========================================
        # Create Attempts for Analytics
        # ==========================================
        self.stdout.write('Creating student attempts...')
        
        # Attempt for CS Exam (Student 1 - Pass)
        student = students[0]
        attempt = ExamAttempt.objects.create(
            student=student,
            exam=cs_exam,
            status='submitted',
            score=20, # 4 correct * 5 marks
            started_at=timezone.now() - timedelta(hours=2),
            completed_at=timezone.now() - timedelta(hours=1),
            remaining_seconds=0,
            is_submitted=True
        )
        
        for q in cs_exam.questions.all():
            correct_choice = q.choices.filter(is_correct=True).first()
            StudentAnswer.objects.create(
                attempt=attempt,
                question=q,
                selected_choice=correct_choice
            )
            
        # Attempt for CS Exam (Student 2 - Fail)
        if len(students) > 1:
            student2 = students[1]
            attempt2 = ExamAttempt.objects.create(
                student=student2,
                exam=cs_exam,
                status='submitted',
                score=5, # 1 correct
                started_at=timezone.now() - timedelta(hours=3),
                completed_at=timezone.now() - timedelta(hours=2),
                remaining_seconds=0,
                is_submitted=True
            )
            
            # Answer only 1 correctly
            questions = list(cs_exam.questions.all())
            correct_choice = questions[0].choices.filter(is_correct=True).first()
            StudentAnswer.objects.create(
                attempt=attempt2,
                question=questions[0],
                selected_choice=correct_choice
            )
            # Wrong answers for others
            for q in questions[1:]:
                wrong_choice = q.choices.filter(is_correct=False).first()
                StudentAnswer.objects.create(
                    attempt=attempt2,
                    question=q,
                    selected_choice=wrong_choice
                )

        # Attempt for History Exam (Student 1 - Mixed)
        student = students[0]
        attempt_hist = ExamAttempt.objects.create(
            student=student,
            exam=hist_exam,
            status='submitted',
            score=4, # Objective score
            started_at=timezone.now() - timedelta(days=1),
            completed_at=timezone.now() - timedelta(days=1, hours=22),
            remaining_seconds=0,
            is_submitted=True
        )
        
        # Objective Answers
        for q in hist_exam.questions.filter(type='objective'):
            correct_choice = q.choices.filter(is_correct=True).first()
            StudentAnswer.objects.create(
                attempt=attempt_hist,
                question=q,
                selected_choice=correct_choice
            )
            
        # Subjective Answers (Ungraded)
        for q in hist_exam.questions.filter(type='subjective'):
            StudentAnswer.objects.create(
                attempt=attempt_hist,
                question=q,
                answer_text="This is a sample essay answer demonstrating knowledge about the topic."
            )

        self.stdout.write(self.style.SUCCESS('Student attempts created.'))

    def create_questions(self, exam, questions_data):
        for i, q_data in enumerate(questions_data, 1):
            question = Question.objects.create(
                exam=exam,
                text=q_data['text'],
                type=q_data['type'],
                marks=q_data['marks'],
                order=i
            )
            
            for c_data in q_data['choices']:
                Choice.objects.create(
                    question=question,
                    text=c_data['text'],
                    is_correct=c_data['is_correct']
                )

