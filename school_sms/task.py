from celery import shared_task
from django.utils import timezone
from django.conf import settings
from django.core.management import call_command
import boto3
import logging
from pathlib import Path
import os
from pickup.models import PickupAuthorization

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

# Initialize S3 Client helper
def get_s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME,
    )

@shared_task
def backup_project_data(backup_type='aws'):
    """
    Backs up the entire database using dumpdata.
    backup_type: 'aws' (upload to S3) or 'local' (keep local only)
    """
    timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
    filename = f"full_backup_{timestamp}.json"
    backup_dir = Path(settings.BASE_DIR) / "backups"
    backup_dir.mkdir(exist_ok=True)
    file_path = backup_dir / filename

    logger.info(f"Starting backup: {filename} ({backup_type})")

    try:
        # Dump all data
        with open(file_path, 'w') as f:
            call_command('dumpdata', exclude=['contenttypes', 'sessions'], stdout=f)
        
        logger.info(f"Local backup created at {file_path}")

        if backup_type == 'aws':
            try:
                s3_client = get_s3_client()
                bucket = settings.AWS_STORAGE_BUCKET_NAME
                folder = getattr(settings, 'AWS_BACKUP_FOLDER', 'backups')
                s3_key = f"{folder}/{filename}"

                s3_client.upload_file(
                    str(file_path),
                    bucket,
                    s3_key
                )
                logger.info(f"Uploaded backup to S3: {s3_key}")
            except Exception as aws_e:
                logger.error(f"AWS Upload failed: {str(aws_e)}")
                # Don't fail the whole task if local backup succeeded, but warn user
                # However, if user explicitly asked for AWS backup, this is a partial failure.
                # For now, we raise it so user knows.
                raise aws_e
            
            # Optionally remove local file after upload if you want to save space, 
            # but user asked for "Local Sync" so we might keep it or manage retention.
            # For now, we keep it.

        return f"Backup successful: {filename}"

    except Exception as e:
        logger.error(f"Backup failed: {str(e)}")
        raise e

@shared_task
def restore_project_data(source_type, source_path):
    """
    Restores database from a backup.
    source_type: 'local' or 'aws'
    source_path: filename (for local) or s3_key (for aws)
    """
    logger.info(f"Starting restore from {source_type}: {source_path}")
    
    local_file_path = None
    
    try:
        if source_type == 'aws':
            s3_client = get_s3_client()
            bucket = settings.AWS_STORAGE_BUCKET_NAME
            filename = os.path.basename(source_path)
            restore_dir = Path(settings.BASE_DIR) / "restores"
            restore_dir.mkdir(exist_ok=True)
            local_file_path = restore_dir / filename
            
            logger.info(f"Downloading from S3: {source_path}")
            s3_client.download_file(bucket, source_path, str(local_file_path))
        else:
            # Local file
            backup_dir = Path(settings.BASE_DIR) / "backups"
            local_file_path = backup_dir / source_path
            if not local_file_path.exists():
                raise FileNotFoundError(f"Backup file not found: {local_file_path}")

        # Perform loaddata
        logger.info(f"Loading data from {local_file_path}")
        call_command('loaddata', str(local_file_path))
        
        logger.info("Restore completed successfully")
        return "Restore successful"

    except Exception as e:
        logger.error(f"Restore failed: {str(e)}")
        raise e
