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
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    payee_type = models.CharField(max_length=20, choices=PAYEE_TYPES)
    reference_code = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.payee_type})" 
    
    def get_id(self):
        if self.user.role in self.PAYEE_TYPES:
            reference_code = f"PAYEE-{self.user.id}/{uuid4().hex[:5].upper()}"
            return reference_code
    
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
            self.reference_code = self.get_id()

        super().save(*args, **kwargs)


class PayeeOnboarding(models.Model):
    payee = models.OneToOneField(Payee, on_delete=models.CASCADE)
    step = models.PositiveSmallIntegerField(default=1)
    completed = models.BooleanField(default=False)


class BankAccount(models.Model):
    payee = models.ForeignKey(Payee, on_delete=models.CASCADE, related_name="bank_accounts")
    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=20)
    account_name = models.CharField(max_length=100)
    is_primary = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_primary:
            qs = BankAccount.objects.filter(
                payee=self.payee,
                is_primary=True
            )
            if self.pk:
                qs = qs.exclude(pk=self.pk)

            qs.update(is_primary=False)

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
    is_taxable = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class SalaryStructure(models.Model):
    name = models.CharField(max_length=100)
    payee_type = models.CharField(max_length=20)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class SalaryStructureItem(models.Model):
    salary_structure = models.ForeignKey(
        SalaryStructure, on_delete=models.CASCADE, related_name="items"
    )
    component = models.ForeignKey(SalaryComponent, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    percentage = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )

    def clean(self):
        if not self.amount and not self.percentage:
            raise ValueError("Either amount or percentage must be set")

    def __str__(self):
        return f"{self.component.name}"
    

class PayrollPeriod(models.Model):
    month = models.PositiveIntegerField()
    year = models.PositiveIntegerField()

    is_generated = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_periods"
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("month", "year")

  
    def __str__(self):
        return f"{self.month}/{self.year}"


class PayrollRecord(models.Model):
    STATUS = (
        ("generated", "Generated"),
        ("approved", "Approved"),
    )

    payee = models.ForeignKey(
        "payroll.Payee",
        on_delete=models.CASCADE,
        related_name="payroll_records"
    )
    payroll_period = models.ForeignKey(
        "payroll.PayrollPeriod",
        on_delete=models.CASCADE,
        related_name="records"
    )

    gross_pay = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00")
    )
    total_deductions = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00")
    )
    net_pay = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00")
    )

    generated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="generated_payrolls"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="generated"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("payee", "payroll_period")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.payee} - {self.payroll_period}"

    # =========================
    # PAYMENT STATE (TRUTH SOURCE)
    # =========================
    def is_fully_paid(self):
    
        return self.successful_transactions.filter(status="success").exists()


    # =========================
    # SAFETY LOCK
    # =========================
    def save(self, *args, **kwargs):
        """
        Prevent modification once payroll period is locked.
        Allows initial creation only.
        """
        if self.pk and self.payroll_period.is_locked:
            raise ValueError("Cannot modify payroll for a locked period.")
        super().save(*args, **kwargs)


class PayrollAuditLog(models.Model):
    action = models.CharField(max_length=255)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.action


class PayeeSalaryStructure(models.Model):
    payee = models.OneToOneField(
        Payee, on_delete=models.CASCADE, related_name="salary_assignment"
    )
    salary_structure = models.ForeignKey(
        SalaryStructure, on_delete=models.PROTECT
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True
    )

    def __str__(self):
        return f"{self.payee} → {self.salary_structure}"



class PayslipItem(models.Model):
    payroll_record = models.ForeignKey(
        PayrollRecord, on_delete=models.CASCADE, related_name="items"
    )
    component_name = models.CharField(max_length=100)
    component_type = models.CharField(
        max_length=20, choices=(("earning", "Earning"), ("deduction", "Deduction"))
    )
    calculation_type = models.CharField(
        max_length=20, choices=(("fixed", "Fixed"), ("percentage", "Percentage"))
    )
    value = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return self.component_name


class PayrollApproval(models.Model):
    payroll_record = models.OneToOneField(
        PayrollRecord, on_delete=models.CASCADE, related_name="approval"
    )
    bursar_approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="+"
    )
    bursar_approved_at = models.DateTimeField(null=True, blank=True)

    admin_approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="+"
    )
    admin_approved_at = models.DateTimeField(null=True, blank=True)

    def is_fully_approved(self):
        return self.bursar_approved_at and self.admin_approved_at


class PaymentBatch(models.Model):
    payroll_period = models.ForeignKey(PayrollPeriod, on_delete=models.PROTECT)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False)

    def __str__(self):
        return f"Batch {self.pk} - {self.payroll_period}"
    


class PayrollGenerationLog(models.Model):
    payroll_period = models.ForeignKey(PayrollPeriod, on_delete=models.CASCADE)
    payee = models.ForeignKey(Payee, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20,
        choices=[("success", "Success"), ("failed", "Failed")]
    )
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)



class PaymentTransaction(models.Model):
    STATUS = (
        ("pending", "Pending"),
        ("success", "Success"),
        ("failed", "Failed"),
    )

    payroll_record = models.OneToOneField(
        PayrollRecord, on_delete=models.PROTECT, related_name="successful_transactions"
    )
    batch = models.ForeignKey(
        PaymentBatch, on_delete=models.PROTECT, related_name="transactions"
    )

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=20)
    account_name = models.CharField(max_length=100)

    paystack_reference = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default="pending")
    failure_reason = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)


class TransferRecipient(models.Model):
    payee = models.OneToOneField(Payee, on_delete=models.CASCADE)
    recipient_code = models.CharField(max_length=100, unique=True)
    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)



class StaffProfile(models.Model):
    payee = models.OneToOneField(Payee, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    date_of_employment = models.DateField()
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return self.payee.user.get_full_name()
    

class PayrollEnrollment(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    payee = models.OneToOneField(Payee, on_delete=models.CASCADE)

    enrolled_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="payroll_enrollments"
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} → Payroll"



class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('APPROVE', 'Approve'),
        ('PAY', 'Pay'),
        ('FAIL', 'Fail'),
        ('RETRY', 'Retry'),
        ('VIEW', 'View'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    object_type = models.CharField(max_length=100)
    object_id = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['object_type', 'object_id']),
        ]

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValueError("Audit logs are immutable")
        super().save(*args, **kwargs)


class PayrollLineItem(models.Model):
    LINE_TYPES = (
        ("earning", "Earning"),
        ("deduction", "Deduction"),
    )

    payroll_record = models.ForeignKey(
        PayrollRecord,
        on_delete=models.CASCADE,
        related_name="line_items"
    )

    component = models.ForeignKey(
        SalaryComponent,
        on_delete=models.PROTECT
    )

    line_type = models.CharField(max_length=20, choices=LINE_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.component.name} - {self.amount}"

