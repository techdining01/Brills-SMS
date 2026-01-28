from tkinter import Widget
from django import forms
from leaves.models import LeaveRequest
from payroll.models import PayeeSalaryStructure, Payee
from payroll.models import BankAccount
    
class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ["leave_type", "start_date", "end_date", "reason"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "reason": forms.Textarea(attrs={"rows": 3}),
        }


class PayeeForm(forms.ModelForm):
    class Meta:
        model = Payee
        fields = [
            "user",
            "payee_type",
        ]
        widgets = {
            "user": forms.Select(
                attrs={'class': 'form-control'}
            ),

        
            "payee_type": forms.Select(
                attrs={'class': 'form-control'}
            ),
        }



class PayrollEnrollmentForm(forms.ModelForm):
    class Meta:
        model = PayeeSalaryStructure
        fields = ["payee", "salary_structure"]
        widgets = {
            "payee": forms.Select(attrs={"class": "form-control"}),
            "salary_structure": forms.Select(attrs={"class": "form-control"}),
        }

    def clean_payee(self):
        payee = self.cleaned_data["payee"]

        if PayeeSalaryStructure.objects.filter(payee=payee).exists():
            raise forms.ValidationError(
                "This payee is already enrolled in payroll."
            )

        return payee


class BankAccountForm(forms.ModelForm):
    class Meta:
        model = BankAccount
        fields = [
            "payee",
            "bank_name",
            "account_number",
            "account_name",
            "is_primary",
        ]
        
        widgets = {
            "payee": forms.Select(attrs={"class": "form-control"}), 
            "bank_name": forms.TextInput(attrs={"class": "form-control"}),
            "account_number": forms.TextInput(attrs={"class": "form-control"}),
            "account_name": forms.TextInput(attrs={"class": "form-control"}),
            "is_primary": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }