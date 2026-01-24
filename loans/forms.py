from django import forms
from .models import LoanApplication

class LoanApplicationForm(forms.ModelForm):
    class Meta:
        model = LoanApplication

        fields = ["loan_type", "loan_amount", "tenure_months"]

        widgets = {
            "loan_type": forms.Select(attrs={
                "class": "form-control",
                "placeholder": "Enter loan type"
            }),
            "loan_amount": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Loan Amount"
            }),
          
            "tenure_months": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Duration in months"
            }),
        }
