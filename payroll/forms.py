from django import forms
from django.forms import inlineformset_factory
from .models import Payee, BankAccount, SalaryStructure, SalaryStructureItem, PayrollPeriod, SalaryComponent

class SalaryComponentForm(forms.ModelForm):
    class Meta:
        model = SalaryComponent
        fields = ['name', 'component_type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Basic Salary, Housing...'}),
            'component_type': forms.Select(attrs={'class': 'form-select'}),
        }

class PayeeForm(forms.ModelForm):
    class Meta:
        model = Payee
        fields = ['user', 'payee_type']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-select'}),
            'payee_type': forms.Select(attrs={'class': 'form-select'}),
        }


from .constants import NIGERIAN_BANKS

class BankAccountForm(forms.ModelForm):
    bank_code = forms.ChoiceField(choices=NIGERIAN_BANKS, widget=forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = BankAccount
        fields = ['bank_code', 'account_number', 'account_name', 'is_primary']
        widgets = {
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

class SalaryStructureForm(forms.ModelForm):
    class Meta:
        model = SalaryStructure
        fields = ['name', 'description', 'is_taxable', 'tax_rate']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'is_taxable': forms.CheckboxInput(attrs={'class': 'form-check-input', 'onchange': 'togglePackageTax(this)'}),
            'tax_rate': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
        }

SalaryItemFormSet = inlineformset_factory(
    SalaryStructure, SalaryStructureItem,
    fields=['component', 'amount'],
    extra=1,
    can_delete=True,
    widgets={
        'component': forms.Select(attrs={'class': 'form-select'}),
        'amount': forms.NumberInput(attrs={'class': 'form-control'}),
    }
)


from django.utils import timezone

class PayrollGenerationForm(forms.ModelForm):
    MONTH_CHOICES = [(i, i) for i in range(1, 13)]
    
    @staticmethod
    def get_year_choices():
        current_year = timezone.now().year
        return [(i, i) for i in range(2024, current_year + 11)] # Up to 10 years in future
    
    month = forms.ChoiceField(choices=MONTH_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    year = forms.ChoiceField(choices=[], widget=forms.Select(attrs={'class': 'form-select'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['year'].choices = self.get_year_choices()
        self.fields['year'].initial = timezone.now().year
        self.fields['month'].initial = timezone.now().month

    class Meta:
        model = PayrollPeriod
        fields = ['month', 'year']
        
    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data
