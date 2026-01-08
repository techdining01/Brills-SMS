from django.db import models
from accounts.models import User
from payroll.models import StaffProfile


class LeaveType(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    is_paid = models.BooleanField(default=True)
    default_days = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class LeaveRequest(models.Model):
    STATUS = (
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    )

    staff = models.ForeignKey(StaffProfile, on_delete=models.CASCADE)
    leave_type = models.ForeignKey(LeaveType, on_delete=models.PROTECT)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS, default="pending")
    approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )


    def __str__(self):
        return f"{self.staff} - {self.leave_type} ({self.start_date} → {self.end_date})"
