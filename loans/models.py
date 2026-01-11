from django.db import models
from django.conf import settings
from decimal import Decimal
from payroll.models import Payee
from django.utils import timezone

class LoanType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)  # in %
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class LoanApplication(models.Model):
    STATUS = (
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("completed", "Completed"),
    )

    payee = models.ForeignKey(Payee, on_delete=models.CASCADE, related_name="loans")
    loan_type = models.ForeignKey(LoanType, on_delete=models.SET_NULL, null=True)
    principal_amount = models.DecimalField(max_digits=12, decimal_places=2)
    interest_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    monthly_deduction = models.DecimalField(max_digits=12, decimal_places=2)
    tenure_months = models.PositiveIntegerField()
    outstanding_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS, default="pending")
    applied_at = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # calculate interest & total
        if not self.pk:  # new loan
            self.interest_amount = (self.principal_amount * (self.loan_type.interest_rate or 0)) / Decimal("100")
            self.total_amount = self.principal_amount + self.interest_amount
            self.outstanding_balance = self.total_amount
            if self.tenure_months:
                self.monthly_deduction = self.total_amount / Decimal(self.tenure_months)
        super().save(*args, **kwargs)

    def approve(self, user):
        if self.status != "pending":
            raise ValueError("Loan is not pending approval.")
        self.status = "approved"
        self.approved_by = user
        self.approved_at = timezone.now()
        self.save()

    def reject(self, user):
        if self.status != "pending":
            raise ValueError("Loan is not pending approval.")
        self.status = "rejected"
        self.approved_by = user
        self.approved_at = timezone.now()
        self.save()

    def __str__(self):
        return f"{self.payee} - {self.loan_type} ({self.status})"

class LoanRepayment(models.Model):
    loan = models.ForeignKey(LoanApplication, on_delete=models.CASCADE, related_name="repayments")
    payroll_record = models.ForeignKey("payroll.PayrollRecord", on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    balance_after = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.loan.payee} - {self.amount} - Balance: {self.balance_after}"
