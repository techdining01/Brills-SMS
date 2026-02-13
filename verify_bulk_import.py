import os
import django
import io
from django.core.files.uploadedfile import SimpleUploadedFile

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_sms.settings')
django.setup()

from exams.models import SchoolClass, Subject
from dashboards.models import QuestionBank, BulkImportJob
from dashboards.bulk_operations import BulkImporter
from accounts.models import User

def verify_import():
    # 1. Setup Data
    print("Setting up data...")
    user = User.objects.first()
    if not user:
        print("No user found, creating dummy user")
        user = User.objects.create(username='test_importer')

    school_class, _ = SchoolClass.objects.get_or_create(name="Primary 1 Verification")
    subject, _ = Subject.objects.get_or_create(name="Mathematics Verification")

    # 2. Create CSV content
    csv_content = f"""text,type,marks,class,subject
"Test Q1 Verification",objective,1,"{school_class.name}","{subject.name}"
"Test Q2 Verification",subjective,5,"{school_class.name}","{subject.name}"
"""
    
    csv_file = SimpleUploadedFile("test_questions.csv", csv_content.encode('utf-8'))

    # 3. Running Import
    print("Running import...")
    job = BulkImporter.import_questions(csv_file, user)
    
    print(f"Job Status: {job.status}")
    print(f"Error Log: {job.error_log}")

    if job.status == 'completed':
        # 4. Verify Data
        q1 = QuestionBank.objects.filter(text="Test Q1 Verification").first()
        if q1:
            print(f"Q1 Found: {q1}")
            print(f"Q1 Class: {q1.school_class.name if q1.school_class else 'None'}")
            print(f"Q1 Subject: {q1.subject.name if q1.subject else 'None'}")
            print(f"Q1 Difficulty: {q1.difficulty}")
            
            if q1.school_class == school_class and q1.subject == subject and q1.difficulty == 'medium':
                print("SUCCESS: Q1 verification passed!")
            else:
                print("FAILURE: Q1 data mismatch.")
        else:
            print("FAILURE: Q1 not found.")
    else:
        print("FAILURE: Job failed.")

if __name__ == "__main__":
    verify_import()
