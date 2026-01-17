from atexit import register
from re import search
from turtle import mode
from django.contrib import admin

from accounts import forms, models
from .models import (
    Payee, BankAccount, PayeeSalaryStructure, PaymentTransaction, SalaryComponent,
    SalaryStructure, SalaryStructureItem, PaymentBatch, PayrollEnrollment,
    PayrollPeriod, PayrollRecord, PayrollAuditLog, PayslipItem, StaffProfile, TransferRecipient
)

from payroll.services.payroll_generation import bulk_generate_payroll


class BankAccountInline(admin.TabularInline):
    model = BankAccount
    extra = 1


@admin.register(Payee)
class PayeeAdmin(admin.ModelAdmin):
    list_display = ("user", "payee_type", "reference_code", "is_active")
    list_filter = ("user__first_name", "payee_type", "is_active")
    search_fields = ("reference_code",)
    inlines = [BankAccountInline]


@admin.register(SalaryComponent)
class SalaryComponentAdmin(admin.ModelAdmin):
    list_display = ("name", "component_type", "is_taxable", "is_active")
    list_filter = ("component_type", "is_active")


class SalaryStructureItemInline(admin.TabularInline):
    model = SalaryStructureItem
    extra = 1


@admin.register(SalaryStructure)
class SalaryStructureAdmin(admin.ModelAdmin):
    list_display = ("name", "payee_type", "created_by", "created_at")
    inlines = [SalaryStructureItemInline]


@admin.register(PayrollPeriod)
class PayrollPeriodAdmin(admin.ModelAdmin):
    list_display = ("month", "year", "is_paid")
    list_filter = ("is_paid",)


@admin.register(PayrollRecord)
class PayrollRecordAdmin(admin.ModelAdmin):
    list_display = (
        "payee", "payroll_period", "gross_pay",
        "total_deductions", "net_pay", "status"
    )
    list_filter = ("status", "payroll_period")
    readonly_fields = ("gross_pay", "total_deductions", "net_pay")


@admin.register(PayrollAuditLog)
class PayrollAuditLogAdmin(admin.ModelAdmin):
    list_display = ("action", "performed_by", "timestamp")
    readonly_fields = ("action", "performed_by", "timestamp", "metadata")


class PayslipItemInline(admin.TabularInline):
    model = PayslipItem
    extra = 0
    readonly_fields = (
        "component_name",
        "component_type",
        "calculation_type",
        "value",
    )



@admin.action(description="Generate payroll for selected period")
def generate_payroll_for_period(modeladmin, request, queryset):
    if queryset.count() != 1:
        modeladmin.message_user(
            request,
            "Please select exactly one payroll period.",
            level="error",
        )
        return

    period = queryset.first()

    if period.is_locked():
        modeladmin.message_user(
            request,
            "This payroll period is locked.",
            level="error",
        )
        return

    result = bulk_generate_payroll(
        payroll_period=period,
        generated_by=request.user,
    )

    modeladmin.message_user(
        request,
        f"Payroll generated. Success: {len(result['success'])}, "
        f"Failed: {len(result['failed'])}",
    )



import csv
from django.http import HttpResponse


@admin.action(description="Export selected payroll records to CSV")
def export_payroll_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="payroll.csv"'

    writer = csv.writer(response)
    writer.writerow([
        "Payee",
        "Payee Type",
        "Period",
        "Gross Pay",
        "Total Deductions",
        "Net Pay",
        "Status",
    ])

    for record in queryset.select_related("payee", "payroll_period"):
        writer.writerow([
            record.payee.user.get_full_name(),
            record.payee.payee_type,
            str(record.payroll_period),
            record.gross_pay,
            record.total_deductions,
            record.net_pay,
            record.status,
        ])

    return response



@admin.action(description="Export payment batch CSV")
def export_payment_batch_csv(modeladmin, request, queryset):
    import csv
    from django.http import HttpResponse

    batch = queryset.first()
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="batch_{batch.id}.csv"'

    writer = csv.writer(response)
    writer.writerow([
        "Payee",
        "Account Number",
        "Bank",
        "Amount",
        "Status",
        "Reference",
    ])

    for tx in batch.transactions.all():
        writer.writerow([
            tx.payroll_record.payee.full_name,
            tx.account_number,
            tx.bank_name,
            tx.amount,
            tx.status,
            tx.paystack_reference,
        ])

    return response

@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ("payee", "phone_number", "address", 
                    "date_of_employment", "is_confirmed")
    search_fields = ("payee__first_name", "phone_number", "address")
    list_filter = ("is_confirmed",)


admin.site.register(BankAccount)
admin.site.add_action(generate_payroll_for_period)
admin.site.add_action(export_payroll_csv)
admin.site.add_action(export_payment_batch_csv)
   

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "payroll_record",
        "amount",
        "status",
        "batch",
        "bank_name",
        "account_number",
        "account_name", 
        "failure_reason",
        "created_at",
    )
    list_filter = ("status", "batch")
    search_fields = ("payroll_record__payee__first_name",)


@admin.register(PayeeSalaryStructure)
class PayeeSalaryStructureAdmin(admin.ModelAdmin):
    list_display = ("payee","salary_structure", "assigned_at","assigned_by")
    search_fields = ("payee__first_name", "salary_structure__name")
    list_filter = ("salary_structure",)



@admin.register(TransferRecipient)
class TransferRecipientAdmin(admin.ModelAdmin):
    list_display = ("payee", "recipient_code", "bank_name", "account_number", "created_at")
    search_fields = ("payee__first_name", "recipient_code", "bank_name", "account_number")
    list_filter = ("bank_name",)


@admin.register(PayrollEnrollment)
class PayrollEnrollmentAdmin(admin.ModelAdmin):
    list_display = ("user", "payee", "enrolled_by", "enrolled_at")
    search_fields = ("user__first_name", "enrolled_by")


@admin.register(PaymentBatch)
class PaymentBatchAdmin(admin.ModelAdmin):
    list_display = ("payroll_period", "created_by", "created_at", "is_processed")
    search_list = ("payroll_period__month", "payroll_period__year", "payroll_period__is_generated",
                   "payroll_period__is_approved", "payroll_period__is_paid", "is_processed",
                    "approved_by" )

 