from django.conf import settings
from django.db import models
from django.utils import timezone


User = settings.AUTH_USER_MODEL


class Payee(models.Model):
    PAYEE_TYPES = (
        ("teacher", "Teacher"),
        ("non_teacher", "Non-Teaching Staff"),
        ("contractor", "Contractor"),
        ("service_provider", "Service Provider"),
    )

    user = models.OneToOneField(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    payee_type = models.CharField(max_length=20, choices=PAYEE_TYPES)
    full_name = models.CharField(max_length=255)
    reference_code = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.payee_type})"


class BankAccount(models.Model):
    payee = models.ForeignKey(Payee, on_delete=models.CASCADE, related_name="bank_accounts")
    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=20)
    account_name = models.CharField(max_length=100)
    is_primary = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_primary:
            BankAccount.objects.filter(
                payee=self.payee, is_primary=True
            ).exclude(id=self.id).update(is_primary=False)
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
    STATUS = (
        ("draft", "Draft"),
        ("locked", "Locked"),
        ("processed", "Processed"),
    )

    month = models.PositiveIntegerField()
    year = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS, default="draft")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("month", "year")

    def is_locked(self):
        return self.status in ("locked", "processed")

    def __str__(self):
        return f"{self.month}/{self.year}"



class PayrollRecord(models.Model):
    STATUS = (
        ("pending", "Pending"),
        ("approved", "Approved"),
    )

    payee = models.ForeignKey(Payee, on_delete=models.CASCADE)
    payroll_period = models.ForeignKey(PayrollPeriod, on_delete=models.CASCADE)
    gross_pay = models.DecimalField(max_digits=12, decimal_places=2)
    total_deductions = models.DecimalField(max_digits=12, decimal_places=2)
    net_pay = models.DecimalField(max_digits=12, decimal_places=2)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("payee", "payroll_period")

    def __str__(self):
        return f"{self.payee} - {self.payroll_period}"
    
    
    def save(self, *args, **kwargs):
        if self.payroll_period.is_locked():
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
        return f"Batch {self.id} - {self.payroll_period}"


class PaymentTransaction(models.Model):
    STATUS = (
        ("pending", "Pending"),
        ("success", "Success"),
        ("failed", "Failed"),
    )

    payroll_record = models.OneToOneField(
        PayrollRecord, on_delete=models.PROTECT
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
        return self.payee.full_name


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

