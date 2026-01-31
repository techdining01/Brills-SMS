from django.core.management.base import BaseCommand
from dashboards.scheduler import process_scheduled_exams, notify_students_before_exam
from exams.models import Exam


class Command(BaseCommand):
    help = 'Process scheduled exams - auto-open and auto-close'

    def add_arguments(self, parser):
        parser.add_argument(
            '--notify',
            action='store_true',
            help='Send notifications to students about upcoming exams',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Processing scheduled exams...'))
        
        # Process scheduled exams
        result = process_scheduled_exams()
        self.stdout.write(
            self.style.SUCCESS(
                f"Opened: {result['opened']}, Closed: {result['closed']}"
            )
        )
        
        # Send notifications if requested
        if options['notify']:
            self.stdout.write(self.style.SUCCESS('Sending notifications...'))
            
            exams = Exam.objects.all()
            total_notified = 0
            
            for exam in exams:
                notified = notify_students_before_exam(exam)
                total_notified += notified
            
            self.stdout.write(
                self.style.SUCCESS(f"Notified {total_notified} students")
            )
