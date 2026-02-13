import os
import django
from django.utils import timezone
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sms.settings')
django.setup()

from dashboards.models import Exam, ExamAttempt
from accounts.models import User

# Get the first student user (assuming the logged-in user is a student)
# In a real scenario, we'd know the user ID, but here I'll just check all students or a specific one if I knew.
# Let's check the first student found.
student = User.objects.filter(role='STUDENT').first()

if not student:
    print("No student user found.")
else:
    print(f"Checking for student: {student.username} (ID: {student.id})")
    print(f"Student Class: {student.student_class}")
    
    now = timezone.now()
    print(f"Current Time (Django): {now}")
    
    # Check all exams
    print("\nAll Exams:")
    all_exams = Exam.objects.all()
    for exam in all_exams:
        print(f"Exam: {exam.title} (ID: {exam.id})")
        print(f"  Class: {exam.school_class}")
        print(f"  Active: {exam.is_active}")
        print(f"  Published: {exam.is_published}")
        print(f"  Start: {exam.start_time}")
        print(f"  End: {exam.end_time}")
        print(f"  Has Ended: {exam.end_time < now}")
        print(f"  Matches Class: {exam.school_class == student.student_class}")
        
        # Check attempts
        attempts = ExamAttempt.objects.filter(student=student, exam=exam)
        print(f"  Attempts: {attempts.count()}")
        for att in attempts:
            print(f"    - Status: {att.status}, Submitted At: {att.completed_at}")

    # Check query used in view
    if student.student_class:
        exams_query = Exam.objects.filter(
            school_class=student.student_class,
            is_active=True,
            is_published=True,
            end_time__gte=now
        ).order_by('start_time')
        
        print(f"\nExams matching query: {exams_query.count()}")
        for e in exams_query:
            print(f"  - {e.title}")
    else:
        print("\nStudent has no class assigned, so query would return nothing.")
