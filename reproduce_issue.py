import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_sms.settings')
django.setup()

from dashboards.analytics import update_exam_analytics, get_exam_statistics
from exams.models import Exam

try:
    exam = Exam.objects.get(id=48)
    print(f"Updating analytics for exam: {exam.title}")
    update_exam_analytics(exam)
    print("Getting statistics...")
    get_exam_statistics(exam)
    print("Success!")
except Exception as e:
    print(f"Error: {e}")
