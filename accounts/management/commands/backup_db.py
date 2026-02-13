import os
import boto3
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from botocore.exceptions import NoCredentialsError

class Command(BaseCommand):
    help = 'Backup the database to AWS S3'

    def handle(self, *args, **options):
        # 1. Check if S3 is configured
        if not getattr(settings, 'USE_S3', False):
            self.stdout.write(self.style.WARNING('S3 is not enabled (USE_S3=False). Skipping cloud backup.'))
            return

        # 2. Identify the database file (assuming SQLite for now)
        db_engine = settings.DATABASES['default']['ENGINE']
        if 'sqlite3' not in db_engine:
            self.stdout.write(self.style.ERROR(f'Backup command currently only supports SQLite. Detected: {db_engine}'))
            return

        db_path = settings.DATABASES['default']['NAME']
        if not os.path.exists(db_path):
            self.stdout.write(self.style.ERROR(f'Database file not found at {db_path}'))
            return

        # 3. Prepare backup filename
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        backup_filename = f"db_backup_{timestamp}.sqlite3"
        s3_path = f"{getattr(settings, 'AWS_BACKUP_FOLDER', 'backups')}/{backup_filename}"

        # 4. Upload to S3
        self.stdout.write(f"Starting backup of {db_path} to S3...")
        
        try:
            s3 = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME
            )
            
            s3.upload_file(str(db_path), settings.AWS_STORAGE_BUCKET_NAME, s3_path)
            
            self.stdout.write(self.style.SUCCESS(f"Successfully backed up database to s3://{settings.AWS_STORAGE_BUCKET_NAME}/{s3_path}"))
            
        except NoCredentialsError:
            self.stdout.write(self.style.ERROR("AWS credentials not found. Please check your .env file."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred during backup: {str(e)}"))
