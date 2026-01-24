from django.contrib import admin

from .models import LoanApplication, LoanRepayment

@admin.register(LoanApplication)
class LoanApplicationAdmin(admin.ModelAdmin):   
    list_display = ("payee", "loan_type", "status", "applied_at")
    list_filter = ("status", "loan_type")
    search_fields = ("payee__username", "loan_type__type")
@admin.register(LoanRepayment)
class LoanRepaymentAdmin(admin.ModelAdmin):  
    list_display = ("loan", "amount_paid", "balance_after")
    search_fields = ("loan__payee__username",)