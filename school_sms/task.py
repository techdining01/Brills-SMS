from celery import shared_task
from django.utils import timezone
from django.conf import settings
from celery import shared_task
from pathlib import Path
from pickup.models import PickupAuthorization
from exams.models import Exam, ExamAttempt
from brillspay.models import PaymentTransaction
import json
import logging

logger = logging.getLogger(__name__)
logger = logging.getLogger("project")

@shared_task
def cleanup_expired_pickups():
    expired = PickupAuthorization.objects.filter(
        expires_at__lt=timezone.now(),
        is_used=False
    )
    count = expired.count()
    expired.update(is_used=True)
    logger.info(f"{count} expired pickups auto-marked as used")
    return f"{count} pickups cleaned"



import boto3
from django.conf import settings
s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_S3_REGION_NAME,
)

@shared_task
def backup_project_data():
    timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
    bucket = settings.AWS_STORAGE_BUCKET_NAME
    folder = settings.AWS_BACKUP_FOLDER

    # 1️⃣ Backup logs
    log_path = Path(settings.BASE_DIR) / "logs/project.log"
    if log_path.exists():
        s3_client.upload_file(
            str(log_path),
            bucket,
            f"{folder}/logs/project_{timestamp}.log"
        )
        logger.info(f"Uploaded project.log to S3 at {timestamp}")

    # 2️⃣ Backup Exams & Attempts
    exams = list(Exam.objects.all().values())
    attempts = list(ExamAttempt.objects.all().values())
    data = {"exams": exams, "attempts": attempts}

    file_path = Path(settings.BASE_DIR) / f"backup_{timestamp}.json"
    with open(file_path, "w") as f:
        json.dump(data, f, default=str)

    s3_client.upload_file(
        str(file_path),
        bucket,
        f"{folder}/backup_{timestamp}.json"
    )
    logger.info(f"Uploaded exams & attempts backup to S3 at {timestamp}")
