from django.utils import timezone
from payroll.models import PayrollApproval, PayrollAuditLog


def approve_by_bursar(payroll_record, user):
    approval, _ = PayrollApproval.objects.get_or_create(
        payroll_record=payroll_record
    )
    approval.bursar_approved_by = user
    approval.bursar_approved_at = timezone.now()
    approval.save()

    PayrollAuditLog.objects.create(
        action="Payroll approved by bursar",
        performed_by=user,
        metadata={"payroll_id": payroll_record.id},
    )


def approve_by_admin(payroll_record, user):
    approval = payroll_record.approval

    if not approval.bursar_approved_at:
        raise ValueError("Bursar approval required first.")

    approval.admin_approved_by = user
    approval.admin_approved_at = timezone.now()
    approval.save()

    PayrollAuditLog.objects.create(
        action="Payroll approved by admin",
        performed_by=user,
        metadata={"payroll_id": payroll_record.id},
    )
