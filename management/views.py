from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from .utils import BackupRestoreManager
import os



# Check if the user is a Superuser before allowing access
@user_passes_test(lambda u: u.is_superuser)
def backup_restore_view(request):
    manager = BackupRestoreManager()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'backup':
            success, msg = manager.create_backup()
        elif action == 'restore':
            # Critical step: Ask for a secondary confirmation in the POST data
            if request.POST.get('confirm_restore') == 'YES':
                success, msg = manager.restore_latest_backup()
            else:
                success, msg = False, "Restore action canceled. Confirmation required."
        else:
            success, msg = False, "Invalid action."
            
        if success:
            messages.success(request, msg)
        else:
            messages.error(request, msg)
            
        return redirect('management:backup_restore')
    latest_file = manager._get_latest_backup_file()
    
    # List all backup files for display
    all_files = [f for f in os.listdir(manager.backup_dir) if f.endswith('.json')]
    all_files.sort(key=lambda x: os.path.getmtime(os.path.join(manager.backup_dir, x)), reverse=True)
    
    return render(request, 'management/backup_restore.html', {
        'latest_file': latest_file,
        'all_files': all_files
    })