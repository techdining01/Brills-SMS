from django import forms
from leaves.models import LeaveRequest, LeaveType


class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ["leave_type", "start_date", "end_date", "reason"]
        widgets = {
            "leave_type": forms.Select(attrs={'class': 'form-control'}),
            "start_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "end_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "reason": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

class LeaveTypeForm(forms.ModelForm):
    class Meta:
        model = LeaveType
        fields = ["name", "annual_days"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "annual_days": forms.TextInput(attrs={"class": "form-control", "type": "number"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].queryset = LeaveType.objects.all()
        self.fields["name"].label = "Leave Type"
        self.fields["annual_days"].label = "Annual days"