from django.contrib.auth import get_user_model
from django import forms
from .models import Payee, SalaryStructure, PayeeSalaryStructure, BankAccount
from django.utils import timezone   

User = get_user_model()

class AdminPayeeCreationForm(forms.ModelForm):

    user = forms.ModelChoiceField(
        queryset=User.objects.all(), 
        required=False, 
        label="Link User Account",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    salary_structure = forms.ModelChoiceField(
        queryset=SalaryStructure.objects.all(), 
        required=False, 
        label="Salary Package",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    class Meta:
        model = Payee
        fields = ['user', 'payee_type', 'salary_structure']

        widgets = {
            'payee_type': forms.Select(attrs={'class': 'form-select'}),
        }

    def save(self, *args, **kwargs):
        payee = super().save(*args, **kwargs)
        structure = self.cleaned_data.get('salary_structure')
        
        if structure:
            PayeeSalaryStructure.objects.update_or_create(
                payee=payee,
                defaults={'salary_structure': structure}
            )
        return payee
    


from .constants import NIGERIAN_BANKS

class AdminBankAccountForm(forms.ModelForm):
    bank_code = forms.ChoiceField(choices=NIGERIAN_BANKS, widget=forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = BankAccount
        fields = ['payee','bank_code', 'account_number', 'account_name', 'is_primary']
        widgets = {
            'payee': forms.Select(attrs={'class': 'form-control'}),
            'bank_code': forms.Select(attrs={'class': 'form-select'}),
            'account_number': forms.TextInput(attrs={'class': 'form-control'}),
            'account_name': forms.TextInput(attrs={'class': 'form-control'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }   
        
    def clean(self):
        cleaned_data = super().clean()
        bank_code = cleaned_data.get('bank_code')
        # Find bank name from constants
        bank_name = dict(NIGERIAN_BANKS).get(bank_code)
        if bank_name:
            self.instance.bank_name = bank_name
        return cleaned_data
