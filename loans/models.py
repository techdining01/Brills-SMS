from django.db import models
from django.conf import settings
from decimal import Decimal
from payroll.models import Payee
from django.utils import timezone


class LoanApplication(models.Model):

    LOAN_TYPES = (
        ("personal", "Personal Loan"),  
        ("housing", "Housing Loan"),
        ("car", "Car Loan"),
        ("education", "Education Loan"),
        ("business", "Business Loan"),
    )   
     
    STATUS = (
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("completed", "Completed"),
    )

    payee = models.ForeignKey(Payee, on_delete=models.CASCADE, related_name="loans")
    loan_type = models.CharField(max_length=100, choices=LOAN_TYPES, default="personal")
    loan_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    monthly_deduction = models.DecimalField(max_digits=12, decimal_places=2)
    tenure_months = models.PositiveIntegerField()
    outstanding_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS, default="pending")
    progress = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # percentage
    applied_at = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:  # new loan
            self.outstanding_balance = self.loan_amount
            if self.tenure_months:
                self.monthly_deduction = self.loan_amount / Decimal(self.tenure_months)
        super().save(*args, **kwargs)

    def approve(self, user):
        if self.status != "pending":
            raise ValueError("Loan must be in pending waiting approval.")
        self.status = "approved"
        self.approved_by = user
        self.approved_at = timezone.now()
        self.save()

    def reject(self, user):
        if self.status != "pending":
            raise ValueError("Loan must be in pending waiting approval.")
        self.status = "rejected"
        self.approved_by = user
        self.approved_at = timezone.now()
        self.save()


    def __str__(self):
        return f"{self.payee} - {self.loan_type} ({self.status})"

class LoanRepayment(models.Model):
    loan = models.ForeignKey(LoanApplication, on_delete=models.CASCADE, related_name="repayments")
    payroll_record = models.ForeignKey("payroll.PayrollRecord", on_delete=models.SET_NULL, null=True, blank=True)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2)
    balance_after = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.loan.payee} - {self.amount} - Balance: {self.balance_after}"

    
   