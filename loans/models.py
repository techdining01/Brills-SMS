from django.db import models
from django.conf import settings
from django.utils import timezone
from payroll.models import Payee, PayrollRecord

User = settings.AUTH_USER_MODEL


class Loan(models.Model):
    STATUS = (
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("completed", "Completed"),
    )

    payee = models.ForeignKey(Payee, on_delete=models.CASCADE)
    principal = models.DecimalField(max_digits=12, decimal_places=2)
    months = models.PositiveIntegerField()
    monthly_deduction = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS, default="pending")
    approved_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    outstanding_balance = models.DecimalField(
        max_digits=12, decimal_places=2
    )

    def save(self, *args, **kwargs):
        if not self.pk:
            self.outstanding_balance = self.amount
        super().save(*args, **kwargs)


    def __str__(self):
        return f"Loan - {self.payee.full_name}"



class LoanRepayment(models.Model):
    loan = models.ForeignKey(
        Loan, on_delete=models.CASCADE, related_name="repayments"
    )
    payroll_record = models.ForeignKey(
        PayrollRecord, on_delete=models.CASCADE
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    balance_after = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)



class LoanRequest(models.Model):
    STATUS = (
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    )

    payee = models.ForeignKey(Payee, on_delete=models.CASCADE)
    requested_amount = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.TextField()

    status = models.CharField(max_length=20, choices=STATUS, default="pending")

    requested_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.payee} - {self.status}"


class LoanSchedule(models.Model):
    loan = models.ForeignKey(
        Loan,
        related_name="schedule",
        on_delete=models.CASCADE
    )
    month = models.PositiveIntegerField()
    principal_component = models.DecimalField(max_digits=10, decimal_places=2)
    total_payment = models.DecimalField(max_digits=10, decimal_places=2)
    balance = models.DecimalField(max_digits=12, decimal_places=2)
    paid = models.BooleanField(default=False)
