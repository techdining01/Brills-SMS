from payroll.models import AuditLog

def log_action(*, user, action, obj, description="", ip=None):
    AuditLog.objects.create(
        user=user,
        action=action,
        object_type=obj.__class__.__name__,
        object_id=str(obj.pk),
        description=description,
        ip_address=ip,
    )
    return log_action