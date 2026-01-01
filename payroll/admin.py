from django.contrib import admin
from .models import (
    Payee, BankAccount, SalaryComponent,
    SalaryStructure, SalaryStructureItem,
    PayrollPeriod, PayrollRecord, PayrollAuditLog, PayslipItem
)

from payroll.services.payroll_generation import bulk_generate_payroll




class BankAccountInline(admin.TabularInline):
    model = BankAccount
    extra = 1


@admin.register(Payee)
class PayeeAdmin(admin.ModelAdmin):
    list_display = ("full_name", "payee_type", "reference_code", "is_active")
    list_filter = ("payee_type", "is_active")
    search_fields = ("full_name", "reference_code")
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
    list_display = ("month", "year", "status")
    list_filter = ("status",)


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


# @admin.register(PayrollRecord)
# class PayrollRecordAdmin(admin.ModelAdmin):
#     list_display = (
#         "payee",
#         "payroll_period",
#         "gross_pay",
#         "total_deductions",
#         "net_pay",
#         "status",
#     )
#     inlines = [PayslipItemInline]
#     readonly_fields = (
#         "payee",
#         "payroll_period",
#         "gross_pay",
#         "total_deductions",
#         "net_pay",
#     )


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


# @admin.register(PayrollPeriod)
# class PayrollPeriodAdmin(admin.ModelAdmin):
#     list_display = ("month", "year", "status")
#     list_filter = ("status",)
#     actions = [generate_payroll_for_period]


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
            record.payee.full_name,
            record.payee.payee_type,
            str(record.payroll_period),
            record.gross_pay,
            record.total_deductions,
            record.net_pay,
            record.status,
        ])

    return response


# @admin.register(PayrollRecord)
# class PayrollRecordAdmin(admin.ModelAdmin):
#     list_display = (
#         "payee",
#         "payroll_period",
#         "gross_pay",
#         "total_deductions",
#         "net_pay",
#         "status",
#     )
#     list_filter = ("status", "payroll_period")
#     actions = [export_payroll_csv]
#     readonly_fields = (
#         "payee",
#         "payroll_period",
#         "gross_pay",
#         "total_deductions",
#         "net_pay",
#     )



# @admin.register(PayrollPeriod)
# class PayrollPeriodAdmin(admin.ModelAdmin):
#     list_display = ("month", "year", "status")
#     actions = ["generate_payroll"]

#     def generate_payroll(self, request, queryset):
#         for period in queryset:
#             result = bulk_generate_payroll(
#                 payroll_period=period,
#                 generated_by=request.user
#             )
#             self.message_user(
#                 request,
#                 f"{period}: Created {result['created']} payroll records "
#                 f"(skipped {result['skipped']})"
#             )

#     generate_payroll.short_description = "Bulk generate payroll"



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



