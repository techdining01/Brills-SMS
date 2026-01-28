from django.contrib import admin
from .models import (
    Payee, BankAccount, SalaryComponent, SalaryStructure, 
    SalaryStructureItem, PayeeSalaryStructure, PayrollPeriod,
    PayrollRecord, PayrollLineItem, PaymentBatch, PaymentTransaction,
    AuditLog
)

@admin.register(Payee)
class PayeeAdmin(admin.ModelAdmin):
    list_display = ('reference_code', 'user', 'payee_type', 'is_active', 'is_payroll_ready')
    list_filter = ('payee_type', 'is_active')
    search_fields = ('reference_code', 'user__username', 'user__email')

@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ('payee', 'bank_name', 'account_number', 'is_primary', 'is_approved')
    list_filter = ('is_primary', 'is_approved', 'bank_name')
    search_fields = ('account_number', 'account_name', 'payee__user__username')
    actions = ['approve_accounts']
    
    def approve_accounts(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, f"{queryset.count()} bank accounts approved.")
    approve_accounts.short_description = "Approve selected bank accounts"

@admin.register(SalaryComponent)
class SalaryComponentAdmin(admin.ModelAdmin):
    list_display = ('name', 'component_type', 'is_active')
    list_filter = ('component_type', 'is_active')

class SalaryStructureItemInline(admin.TabularInline):
    model = SalaryStructureItem
    extra = 1

@admin.register(SalaryStructure)
class SalaryStructureAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_taxable', 'tax_rate', 'created_at')
    list_filter = ('is_taxable',)
    inlines = [SalaryStructureItemInline]

@admin.register(PayeeSalaryStructure)
class PayeeSalaryStructureAdmin(admin.ModelAdmin):
    list_display = ('payee', 'salary_structure', 'assigned_at')
    list_filter = ('salary_structure',)

@admin.register(PayrollPeriod)
class PayrollPeriodAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_generated', 'is_locked', 'is_approved_by_bursar', 'is_approved_by_admin')
    list_filter = ('is_generated', 'is_locked', 'year', 'month')
    actions = ['lock_periods']
    
    def lock_periods(self, request, queryset):
        queryset.update(is_locked=True)
        self.message_user(request, f"{queryset.count()} periods locked.")
    lock_periods.short_description = "Lock selected periods"

@admin.register(PayrollRecord)
class PayrollRecordAdmin(admin.ModelAdmin):
    list_display = ('payee', 'payroll_period', 'gross_pay', 'total_deductions', 'net_pay', 'is_paid')
    list_filter = ('payroll_period',)
    search_fields = ('payee__user__username', 'payee__reference_code')

@admin.register(PayrollLineItem)
class PayrollLineItemAdmin(admin.ModelAdmin):
    list_display = ('payroll_record', 'name', 'amount', 'is_deduction')
    list_filter = ('is_deduction',)

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('paystack_reference', 'payroll_record', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('paystack_reference', 'transfer_code')

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'model_name', 'object_id', 'timestamp')
    list_filter = ('action', 'model_name', 'timestamp')
    search_fields = ('description', 'object_id')
    readonly_fields = ('user', 'action', 'model_name', 'object_id', 'description', 'timestamp')
