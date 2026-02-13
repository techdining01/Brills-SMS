from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from exams.models import SchoolClass, Subject, Exam, Question, Choice
import datetime
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with sample exam data for all classes'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting seeding process...')

        # 1. Clean existing data
        self.stdout.write('Deleting existing exams...')
        Exam.objects.all().delete()
        # Note: Cascade deletes questions, choices, attempts

        # 2. Get Admin User
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            self.stdout.write('Creating superuser...')
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='adminpassword',
                role='ADMIN'
            )

        # 3. Ensure Classes Exist (Fetch all)
        classes = SchoolClass.objects.all()
        if not classes.exists():
            self.stdout.write('No classes found. Creating defaults...')
            default_classes = [
                {'name': 'JSS 1', 'level': 'junior_secondary'},
                {'name': 'JSS 2', 'level': 'junior_secondary'},
                {'name': 'JSS 3', 'level': 'junior_secondary'},
                {'name': 'SSS 1', 'level': 'senior_secondary'},
                {'name': 'SSS 2', 'level': 'senior_secondary'},
                {'name': 'SSS 3', 'level': 'senior_secondary'},
            ]
            for cls_data in default_classes:
                SchoolClass.objects.create(
                    name=cls_data['name'], 
                    level=cls_data['level'],
                    academic_year='2024/2025',
                    teacher=admin_user
                )
            classes = SchoolClass.objects.all()

        # 4. Ensure Subjects Exist
        subject_names = [
            'Mathematics', 'English Language', 'Basic Science', 
            'Civic Education', 'Biology', 'Chemistry', 'Physics', 
            'Economics', 'Government', 'Geography'
        ]
        
        all_subjects = []
        for name in subject_names:
            sub, _ = Subject.objects.get_or_create(
                name=name,
                defaults={
                    'description': f'{name} Subject',
                    'created_by': admin_user
                }
            )
            all_subjects.append(sub)

        # 5. Create Exams for EACH class
        for school_class in classes:
            self.stdout.write(f'Processing Class: {school_class.name}')
            
            # Ensure class has subjects attached
            # (In many schemas M2M is explicit, here we just make sure there are subjects relevant)
            # We will pick 3 random subjects for this class
            
            selected_subjects = random.sample(all_subjects, 3)
            
            for subject in selected_subjects:
                # Add subject to class if not already (logic from original View/Model usually handles this, but doing it here for safety)
                subject.classes.add(school_class)

                # Create Exam
                exam_title = f"{subject.name} - {school_class.name} Term 1 Exam"
                
                exam = Exam.objects.create(
                    title=exam_title,
                    school_class=school_class,
                    created_by=admin_user,
                    duration=60,
                    start_time=timezone.now(),
                    end_time=timezone.now() + datetime.timedelta(days=30),
                    is_published=True,
                    allow_retake=True,
                    passing_marks=50
                )
                
                self.add_questions(exam, subject.name)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully seeded exams for {classes.count()} classes.'))

    def add_questions(self, exam, subject_name):
        # Generic questions to seed
        base_questions = [
            {
                'text': f'What is the basics of {subject_name}?',
                'type': 'objective',
                'marks': 5,
                'choices': [
                    {'text': 'Option A', 'is_correct': False},
                    {'text': 'Option B', 'is_correct': True},
                    {'text': 'Option C', 'is_correct': False},
                    {'text': 'Option D', 'is_correct': False},
                ]
            },
            {
                'text': f'Explain the importance of {subject_name}.',
                'type': 'subjective',
                'marks': 10,
                'choices': []
            },
            {
                'text': 'True or False: This is a difficult subject?',
                'type': 'objective',
                'marks': 2,
                'choices': [
                    {'text': 'True', 'is_correct': True},
                    {'text': 'False', 'is_correct': False},
                ]
            }
        ]
        
        for idx, q_data in enumerate(base_questions):
            question = Question.objects.create(
                exam=exam,
                text=q_data['text'],
                type=q_data['type'],
                marks=q_data['marks'],
                order=idx + 1
            )
            
            for choice_data in q_data['choices']:
                Choice.objects.create(
                    question=question,
                    text=choice_data['text'],
                    is_correct=choice_data['is_correct']
                )
