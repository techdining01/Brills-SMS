# school_sms/management/commands/seed_data.py (CORRECTED)

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from datetime import datetime, timedelta

# Import all models needed for seeding
from sms.models import SchoolClass, Subject, Exam, Question, Choice
from pickup.models import PickupCode 
from brillspay.models import Product, Category # NOTE: Import Category here!

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with essential dummy data for testing the SMS features.'

    def handle(self, *args, **options):
        
        self.stdout.write(self.style.SUCCESS("--- Starting BrillsPay SMS Seed Data Creation (V2) ---"))
        
        with transaction.atomic():
            self.stdout.write(self.style.WARNING("Clearing existing data..."))
            
            # Clear data in the correct dependency order
            PickupCode.objects.all().delete()
            Exam.objects.all().delete()
            Subject.objects.all().delete()
            Product.objects.all().delete()
            Category.objects.all().delete() # Delete Categories first
            SchoolClass.objects.all().delete()
            User.objects.all().exclude(is_superuser=True).delete()
            self.stdout.write(self.style.SUCCESS("Data cleared."))

            # 1. CREATE SCHOOL STRUCTURE
            self.stdout.write("Creating School Structure (Class & Subjects)...")
            
            JSS1 = SchoolClass.objects.create(name='JSS1', academic_year=2025/2026)
            JSS2 = SchoolClass.objects.create(name='JSS2', academic_year=2025/2026)

            math = Subject.objects.create(name='Mathematics', description='Basic and advanced algebra.')
            
            self.stdout.write(self.style.SUCCESS(f"Created {SchoolClass.objects.count()} classes."))


            # 2. CREATE E-COMMERCE CATEGORIES (REQUIRED BY PRODUCT)
            self.stdout.write("Creating E-commerce Categories...")
            
            cat_uniform = Category.objects.create(name='Uniforms')
            cat_book = Category.objects.create(name='Textbooks')
            cat_supply = Category.objects.create(name='School Supplies')
            
            self.stdout.write(self.style.SUCCESS(f"Created {Category.objects.count()} categories."))


            # 3. CREATE USERS
            self.stdout.write("Creating Test Users...")
            
            # STAFF
            staff = User.objects.create_user(
                username='staff', email='staff@sms.com', password='password',
                first_name='Maria', last_name='Stafford', role=User.Role.STAFF, is_staff=True
            )

            # PARENT
            parent = User.objects.create_user(
                username='parent', email='parent@sms.com', password='password',
                first_name='Patricia', last_name='Parental', role=User.Role.PARENT
            )

            # STUDENT (student_class is a ForeignKey, parents is ManyToMany)
            student = User.objects.create_user(
                username='student', email='student@sms.com', password='password',
                first_name='Sammy', last_name='Student', role=User.Role.STUDENT,
                student_class=JSS1 # Link to the SchoolClass object
            )
            # Link the student to the parent (ManyToMany relationship)
            student.parents.add(parent)
            student.save()
            
            self.stdout.write(self.style.SUCCESS("Created staff, parent, and student users."))


            # 4. CREATE EXAM DATA
            exam = Exam.objects.create(
                title='Math Midterm 2025', 
                subject=math, 
                duration_minutes=60, 
                school_class=JSS1,
                created_by=staff
            )
            q1 = Question.objects.create(exam=exam, text="What is the result of 2 + 2?", question_type="objective", marks=5)
            Choice.objects.create(question=q1, text="3",is_correct=False)
            Choice.objects.create(question=q1, text="4",is_correct=True)
            Choice.objects.create(question=q1, text="5",is_correct=False)

            q2 = Question.objects.create(exam=exam, text="Solve for x: 3x = 9", question_type="objective", marks=5)

            Choice.objects.create(question=q2, text="x = 2",is_correct=False)
            Choice.objects.create(question=q2, text="x = 3",is_correct=True)
            Choice.objects.create(question=q2, text="x = 4",is_correct=False)
            self.stdout.write(self.style.SUCCESS("Created Math Exam and questions."))

            # 5. CREATE E-COMMERCE PRODUCTS (Link to Category FK)
            Product.objects.create(
                name="School Uniform Shirt (Size M)",
                category=cat_uniform, # LINKED
                description="Standard medium size school uniform shirt.",
                price=25.00,
                stock_quantity=50
            )
            Product.objects.create(
                name="Advanced Math Textbook",
                category=cat_book, # LINKED
                description="Textbook for Class A Mathematics.",
                price=45.50,
                stock_quantity=15
            )
            self.stdout.write(self.style.SUCCESS(f"Created {Product.objects.count()} products, linked to categories."))


            # 6. CREATE ACTIVE PICKUP CODE
            PickupCode.objects.create(
                parent=parent,
                student=student,
                expires_at=datetime.now() + timedelta(hours=1)
            )
            self.stdout.write(self.style.SUCCESS("Created one active PickupCode."))

        self.stdout.write(self.style.SUCCESS("\nSeed Data Creation Complete!"))
        self.stdout.write(self.style.WARNING("Use 'python manage.py seed_data' to rerun."))