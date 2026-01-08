from django import forms
from leaves.models import LeaveRequest
from django import forms
from .models import Payee, StaffProfile, SalaryStructure

class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ["leave_type", "start_date", "end_date", "reason"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "reason": forms.Textarea(attrs={"rows": 3}),
        }


class PayrollEnrollmentForm(forms.Form):
    full_name = forms.CharField()
    payee_type = forms.ChoiceField(choices=Payee.PAYEE_TYPES)
    salary_structure = forms.ModelChoiceField(queryset=SalaryStructure.objects.all())
