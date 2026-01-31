from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from exams.models import (
    SchoolClass, Subject, Exam, Question, Choice, ExamAttempt, 
    StudentAnswer, Broadcast, Notification, SubjectiveMark
)
from datetime import datetime, timedelta
from django.utils import timezone
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate database with comprehensive demo data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting comprehensive demo data population...'))

        # ==========================================
        # 1. Create Users
        # ==========================================
        self.stdout.write('Creating users...')
        
        # Admin
        admin, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'first_name': 'System',
                'last_name': 'Administrator',
                'role': User.Role.ADMIN,
                'is_staff': True,
                'is_superuser': True
            }
        )
        admin.set_password('admin')
        admin.save()

        # Teachers
        teacher1, _ = User.objects.get_or_create(
            username='teacher',
            defaults={
                'email': 'teacher@example.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'role': User.Role.TEACHER,
                'is_approved': True
            }
        )
        teacher1.set_password('teacher')
        teacher1.save()

        teacher2, _ = User.objects.get_or_create(
            username='teacher2',
            defaults={
                'email': 'teacher2@example.com',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'role': User.Role.TEACHER,
                'is_approved': True
            }
        )
        teacher2.set_password('teacher')
        teacher2.save()

        # Students
        students = []
        for i in range(1, 6):
            s, _ = User.objects.get_or_create(
                username=f'student{i}',
                defaults={
                    'email': f'student{i}@example.com',
                    'first_name': f'Student',
                    'last_name': f'{i}',
                    'role': User.Role.STUDENT,
                    'is_approved': True
                }
            )
            s.set_password('student')
            s.save()
            students.append(s)

        # Parent
        parent, _ = User.objects.get_or_create(
            username='parent',
            defaults={
                'email': 'parent@example.com',
                'first_name': 'Mary',
                'last_name': 'Parent',
                'role': User.Role.PARENT,
                'is_approved': True
            }
        )
        parent.set_password('parent')
        parent.children.add(students[0]) # Add student1 as child
        parent.save()

        # ==========================================
        # 2. Create Classes and Subjects
        # ==========================================
        self.stdout.write('Creating classes and subjects...')
        
        class1, _ = SchoolClass.objects.get_or_create(
            name='JSS 1 A',
            defaults={
                'level': 'junior_secondary',
                'academic_year': '2025/2026',
                'teacher': teacher1,
                'description': 'Junior Secondary School Class 1A'
            }
        )

        class2, _ = SchoolClass.objects.get_or_create(
            name='SSS 2 Science',
            defaults={
                'level': 'senior_secondary',
                'academic_year': '2025/2026',
                'teacher': teacher2,
                'description': 'Senior Secondary School Class 2 Science'
            }
        )

        # Assign students to classes
        for s in students[:3]:
            s.student_class = class1
            s.save()
        
        for s in students[3:]:
            s.student_class = class2
            s.save()

        # Subjects
        math, _ = Subject.objects.get_or_create(
            name='Mathematics',
            defaults={'department': 'STEM', 'created_by': admin, 'is_active': True}
        )
        math.classes.add(class1, class2)

        english, _ = Subject.objects.get_or_create(
            name='English Language',
            defaults={'department': 'Arts', 'created_by': admin, 'is_active': True}
        )
        english.classes.add(class1, class2)

        science, _ = Subject.objects.get_or_create(
            name='Basic Science',
            defaults={'department': 'STEM', 'created_by': admin, 'is_active': True}
        )
        science.classes.add(class1)

        # ==========================================
        # 3. Create Exams
        # ==========================================
        self.stdout.write('Creating exams...')
        
        now = timezone.now()

        # Exam 1: Active Exam (Math)
        exam1, _ = Exam.objects.get_or_create(
            title='JSS 1 Math Mid-Term',
            defaults={
                'school_class': class1,
                'created_by': teacher1,
                'duration': 60,
                'start_time': now - timedelta(days=1),
                'end_time': now + timedelta(days=7),
                'is_active': True,
                'is_published': True
            }
        )

        # Exam 2: Ended Exam (English)
        exam2, _ = Exam.objects.get_or_create(
            title='JSS 1 English Quiz',
            defaults={
                'school_class': class1,
                'created_by': teacher1,
                'duration': 30,
                'start_time': now - timedelta(days=10),
                'end_time': now - timedelta(days=1),
                'is_active': True,
                'is_published': True
            }
        )

        # Exam 3: Draft Exam (Science)
        exam3, _ = Exam.objects.get_or_create(
            title='Basic Science Final',
            defaults={
                'school_class': class1,
                'created_by': teacher1,
                'duration': 90,
                'start_time': now + timedelta(days=5),
                'end_time': now + timedelta(days=6),
                'is_active': True,
                'is_published': False
            }
        )

        # ==========================================
        # 4. Create Questions
        # ==========================================
        self.stdout.write('Creating questions...')

        # Questions for Exam 1 (Math)
        q1_1, _ = Question.objects.get_or_create(
            exam=exam1,
            text='What is 2 + 2?',
            defaults={'type': 'objective', 'marks': 2, 'order': 1}
        )
        Choice.objects.get_or_create(question=q1_1, text='3', is_correct=False)
        Choice.objects.get_or_create(question=q1_1, text='4', is_correct=True)
        Choice.objects.get_or_create(question=q1_1, text='5', is_correct=False)

        q1_2, _ = Question.objects.get_or_create(
            exam=exam1,
            text='Solve for x: 2x = 10',
            defaults={'type': 'objective', 'marks': 3, 'order': 2}
        )
        Choice.objects.get_or_create(question=q1_2, text='5', is_correct=True)
        Choice.objects.get_or_create(question=q1_2, text='10', is_correct=False)
        Choice.objects.get_or_create(question=q1_2, text='2', is_correct=False)

        q1_3, _ = Question.objects.get_or_create(
            exam=exam1,
            text='Explain the Pythagorean theorem.',
            defaults={'type': 'subjective', 'marks': 5, 'order': 3}
        )

        # Questions for Exam 2 (English)
        q2_1, _ = Question.objects.get_or_create(
            exam=exam2,
            text='What is a noun?',
            defaults={'type': 'objective', 'marks': 2, 'order': 1}
        )
        Choice.objects.get_or_create(question=q2_1, text='Action word', is_correct=False)
        Choice.objects.get_or_create(question=q2_1, text='Name of person, place, or thing', is_correct=True)

        q2_2, _ = Question.objects.get_or_create(
            exam=exam2,
            text='Write a short essay about your holiday.',
            defaults={'type': 'subjective', 'marks': 10, 'order': 2}
        )

        # ==========================================
        # 5. Create Attempts and Results
        # ==========================================
        self.stdout.write('Creating attempts and results...')

        # Student 1 takes Exam 1 (Completed)
        attempt1, _ = ExamAttempt.objects.get_or_create(
            student=students[0],
            exam=exam1,
            defaults={
                'completed_at': now - timedelta(hours=1),
                'score': 5.0, # Partial score (only objective graded automatically)
                'status': 'submitted',
                'is_submitted': True,
                'remaining_seconds': 0
            }
        )
        
        # Answers for Attempt 1
        StudentAnswer.objects.get_or_create(
            attempt=attempt1,
            question=q1_1,
            defaults={'selected_choice': Choice.objects.get(question=q1_1, text='4')}
        )
        StudentAnswer.objects.get_or_create(
            attempt=attempt1,
            question=q1_2,
            defaults={'selected_choice': Choice.objects.get(question=q1_2, text='5')}
        )
        ans_sub, _ = StudentAnswer.objects.get_or_create(
            attempt=attempt1,
            question=q1_3,
            defaults={'answer_text': 'It states that a^2 + b^2 = c^2 for a right-angled triangle.'}
        )

        # Teacher grades the subjective answer
        SubjectiveMark.objects.get_or_create(
            answer=ans_sub,
            defaults={
                'score': 4,
                'marked_by': teacher1
            }
        )
        # Update attempt score to include subjective
        attempt1.score = 9.0 
        attempt1.save()


        # Student 2 takes Exam 1 (In Progress)
        ExamAttempt.objects.get_or_create(
            student=students[1],
            exam=exam1,
            defaults={
                'status': 'in_progress',
                'is_submitted': False,
                'remaining_seconds': 1800
            }
        )

        # Student 1 takes Exam 2 (Submitted, waiting for grading)
        attempt2, _ = ExamAttempt.objects.get_or_create(
            student=students[0],
            exam=exam2,
            defaults={
                'completed_at': now - timedelta(days=2, minutes=20),
                'score': 2.0, # Objective only
                'status': 'submitted',
                'is_submitted': True,
                'remaining_seconds': 0
            }
        )
        StudentAnswer.objects.get_or_create(
            attempt=attempt2,
            question=q2_1,
            defaults={'selected_choice': Choice.objects.get(question=q2_1, text='Name of person, place, or thing')}
        )
        StudentAnswer.objects.get_or_create(
            attempt=attempt2,
            question=q2_2,
            defaults={'answer_text': 'My holiday was fun...'}
        )

        # ==========================================
        # 6. Broadcasts and Notifications
        # ==========================================
        self.stdout.write('Creating broadcasts...')

        Broadcast.objects.get_or_create(
            title='Welcome to the new term',
            sender=admin,
            defaults={
                'message': 'Welcome back students! Please check your schedules.',
                'target_class': None # All students
            }
        )

        Broadcast.objects.get_or_create(
            title='Math Assignment Due',
            sender=teacher1,
            defaults={
                'message': 'Remember to submit your math assignment by Friday.',
                'target_class': class1
            }
        )

        Notification.objects.get_or_create(
            recipient=students[0],
            sender=admin,
            title='Exam Graded',
            message='Your JSS 1 Math Mid-Term has been graded.'
        )

        self.stdout.write(self.style.SUCCESS('\n✓ Comprehensive demo data population completed successfully!'))
        self.stdout.write(self.style.WARNING('\nDemo Credentials (Password is username for all):'))
        self.stdout.write(self.style.WARNING('  Admin:    admin'))
        self.stdout.write(self.style.WARNING('  Teacher:  teacher'))
        self.stdout.write(self.style.WARNING('  Student:  student1 (to student5)'))
        self.stdout.write(self.style.WARNING('  Parent:   parent'))
