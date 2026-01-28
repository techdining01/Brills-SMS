from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from payroll.models import Payee

User = settings.AUTH_USER_MODEL

class LeaveType(models.Model):
    name = models.CharField(max_length=50)
    annual_days = models.PositiveIntegerField()

    def __str__(self):
        return self.name

    @classmethod
    def get_default_annual_leave_type(cls):
        return cls.objects.get_or_create(name="Annual Leave", defaults={"annual_days": 20})[0]


class LeaveRequest(models.Model):
    STATUS = (
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    )

    payee = models.ForeignKey(Payee, on_delete=models.CASCADE)
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)

    start_date = models.DateField()
    end_date = models.DateField()

    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default="pending")

    reviewed_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def duration(self):
        return (self.end_date - self.start_date).days + 1

    def clean(self):
        # prevent overlapping approved leave
        if not hasattr(self, 'payee') or self.payee is None:
            return

        overlaps = LeaveRequest.objects.filter(
            payee=self.payee,
            status="approved",
            start_date__lte=self.end_date,
            end_date__gte=self.start_date,
        ).exclude(id=self.pk)

        if overlaps.exists():
            raise ValidationError("Overlapping approved leave exists.")

    def __str__(self):
        return f"{self.payee} - {self.leave_type} ({self.status})"
