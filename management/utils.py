# management/utils.py
import subprocess
import os
from django.conf import settings
from django.utils import timezone

class BackupRestoreManager:
    """Handles executing Django's dumpdata and loaddata commands."""
    
    def __init__(self):
        self.backup_dir = settings.BACKUP_ROOT
        
    def _get_latest_backup_file(self):
        """Finds the most recent backup file in the directory."""
        files = [f for f in os.listdir(self.backup_dir) if f.endswith('.json')]
        if not files:
            return None
        # Sort files by creation/modification time (or use a named format)
        files.sort(key=lambda x: os.path.getmtime(os.path.join(self.backup_dir, x)), reverse=True)
        return files[0]

    def create_backup(self):
        """Creates a new JSON backup file using dumpdata."""
        timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
        filename = f"backup_{timestamp}.json"
        filepath = os.path.join(self.backup_dir, filename)
        
        # Use subprocess to run the Django management command
        try:
            # We exclude session and contenttypes apps for cleaner backups
            result = subprocess.run(
                ['python', 'manage.py', 'dumpdata', '--indent=2', 
                 '--exclude', 'sessions', 
                 '--exclude', 'contenttypes', 
                 '--output', filepath],
                capture_output=True,
                text=True,
                check=True # Raise exception on non-zero exit code
            )
            return True, f"Backup successful: {filename}"
        except subprocess.CalledProcessError as e:
            return False, f"Backup failed: {e.stderr}"
        except FileNotFoundError:
            return False, "Python or manage.py command not found. Check environment."

    def restore_latest_backup(self):
        """Restores data from the latest backup file using loaddata."""
        latest_file = self._get_latest_backup_file()
        
        if not latest_file:
            return False, "No backup files found to restore."
            
        filepath = os.path.join(self.backup_dir, latest_file)
        
        # Confirmation/Warning: This will overwrite current data.
        # Note: In a real environment, you'd halt all processes first.
        try:
            result = subprocess.run(
                ['python', 'manage.py', 'loaddata', filepath],
                capture_output=True,
                text=True,
                check=True
            )
            return True, f"Restore successful from: {latest_file}"
        except subprocess.CalledProcessError as e:
            return False, f"Restore failed: {e.stderr}"