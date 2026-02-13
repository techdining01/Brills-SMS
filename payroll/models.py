from django.conf import settings
from django.db import models
from django.utils import timezone
from decimal import Decimal
from uuid import uuid4

User = settings.AUTH_USER_MODEL

class Payee(models.Model):
    PAYEE_TYPES = (
        ("admin", "Admin Staff"),
        ("teacher", "Teacher"),
        ("non_teacher", "Non-Teaching Staff"),
        ("contractor", "Contractor"),
        ("service_provider", "Service Provider"),
    )

    user = models.OneToOneField(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="payee_profile"
    )
    payee_type = models.CharField(max_length=20, choices=PAYEE_TYPES)
    reference_code = models.CharField(max_length=50, unique=True, blank=True)
    
    # Merged StaffProfile fields
    is_confirmed = models.BooleanField(default=False)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        name = self.user.get_full_name() if self.user else "No User"
        return f"{name} ({self.get_payee_type_display()})"
    
    def generate_reference(self):
        return f"PAYEE-{uuid4().hex[:8].upper()}"
    
    def has_primary_bank(self):
        return self.bank_accounts.filter(is_primary=True).exists()

    def has_salary_structure(self):
        return hasattr(self, "salary_assignment")

    def is_payroll_ready(self):
        return all([
            self.is_active,
            self.has_primary_bank(),
            self.has_salary_structure(),
        ])

    def save(self, *args, **kwargs):
        if not self.reference_code:
            self.reference_code = self.generate_reference()
        super().save(*args, **kwargs)


class BankAccount(models.Model):
    payee = models.ForeignKey(Payee, on_delete=models.CASCADE, related_name="bank_accounts")
    bank_name = models.CharField(max_length=100)
    bank_code = models.CharField(max_length=20, blank=True, help_text="Bank code for Paystack transfers")
    account_number = models.CharField(max_length=20)
    account_name = models.CharField(max_length=100)
    recipient_code = models.CharField(max_length=100, blank=True, help_text="Paystack Transfer Recipient Code")
    is_primary = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)

    class Meta:
        unique_together = ('payee', 'account_number')

    def save(self, *args, **kwargs):
        if self.is_primary:
            # Demote other primary accounts for this payee
            BankAccount.objects.filter(payee=self.payee, is_primary=True).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.bank_name} - {self.account_number}"


class SalaryComponent(models.Model):
    COMPONENT_TYPES = (
        ("earning", "Earning"),
        ("deduction", "Deduction"),
    )

    name = models.CharField(max_length=100)
    component_type = models.CharField(max_length=20, choices=COMPONENT_TYPES)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class SalaryStructure(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_taxable = models.BooleanField(default=False)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'), help_text="Tax percentage applied to total gross")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class SalaryStructureItem(models.Model):
    salary_structure = models.ForeignKey(
        SalaryStructure, on_delete=models.CASCADE, related_name="items"
    )
    component = models.ForeignKey(SalaryComponent, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    def __str__(self):
        return f"{self.component.name} - {self.amount}"


class PayeeSalaryStructure(models.Model):
    payee = models.OneToOneField(
        Payee, on_delete=models.CASCADE, related_name="salary_assignment"
    )
    salary_structure = models.ForeignKey(
        SalaryStructure, on_delete=models.PROTECT
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.payee} -> {self.salary_structure}"


class PayrollPeriod(models.Model):
    month = models.PositiveIntegerField()
    year = models.PositiveIntegerField()

    is_generated = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    
    # Approval Workflow
    is_approved_by_bursar = models.BooleanField(default=False)
    is_approved_by_admin = models.BooleanField(default=False)

    class Meta:
        unique_together = ("month", "year")
        ordering = ["-year", "-month"]

    def __str__(self):
        return f"{self.month}/{self.year}"
    
    @property
    def is_fully_approved(self):
        return self.is_approved_by_bursar and self.is_approved_by_admin


class PayrollRecord(models.Model):
    payee = models.ForeignKey(Payee, on_delete=models.PROTECT, related_name="payroll_records")
    payroll_period = models.ForeignKey(PayrollPeriod, on_delete=models.PROTECT, related_name="records")

    gross_pay = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    
    # Deductions
    loan_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"), help_text="Total loan deductions from external Loan App")
    tax_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    other_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    
    total_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    net_pay = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    # Processing Info
    is_processed = models.BooleanField(default=False)
    processing_error = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("payee", "payroll_period")

    def __str__(self):
        return f"{self.payee} - {self.net_pay}"

    def calculate_net_pay(self):
        self.total_deductions = self.loan_deductions + self.tax_deductions + self.other_deductions
        self.net_pay = self.gross_pay - self.total_deductions
        return self.net_pay
    
    def is_paid(self):
        return self.transactions.filter(status='success').exists()


class PayrollLineItem(models.Model):
    payroll_record = models.ForeignKey(PayrollRecord, on_delete=models.CASCADE, related_name="line_items")
    name = models.CharField(max_length=100) # e.g. "Basic Salary", "Housing Allowance", "Loan Repayment"
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    is_deduction = models.BooleanField(default=False)
    
    def __str__(self):
        sign = "-" if self.is_deduction else "+"
        return f"{self.name}: {sign}{self.amount}"


class PaymentBatch(models.Model):
    payroll_period = models.ForeignKey(PayrollPeriod, on_delete=models.PROTECT)
    reference = models.CharField(max_length=50, unique=True)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"BATCH-{uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class PaymentTransaction(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("success", "Success"),
        ("failed", "Failed"),
    )

    payroll_record = models.ForeignKey(PayrollRecord, on_delete=models.PROTECT, related_name="transactions")
    batch = models.ForeignKey(PaymentBatch, on_delete=models.PROTECT, related_name="transactions", null=True, blank=True)
    
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="NGN")
    
    # Paystack Details
    paystack_reference = models.CharField(max_length=100, blank=True, unique=True)
    transfer_code = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    failure_reason = models.TextField(blank=True)
    response_data = models.JSONField(default=dict, blank=True) # Full response from Paystack
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.paystack_reference} - {self.status}"


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('APPROVE', 'Approve'),
        ('PAY', 'Pay'),
        ('FAIL', 'Fail'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} {self.action} {self.model_name}"

class SchoolSettings(models.Model):
    name = models.CharField(max_length=255, default="Our School")
    address = models.TextField(blank=True)
    logo = models.ImageField(upload_to='school_logos/', null=True, blank=True)

    class Meta:
        verbose_name_plural = "School Settings"

    def __str__(self):
        return self.name

    @classmethod
    def get_settings(cls):
        settings, created = cls.objects.get_or_create(id=1)
        return settings
