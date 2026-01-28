from decimal import Decimal
import requests
from django.conf import settings
from payroll.models import PayrollPeriod
from loans.models import LoanApplication
from django.db.models import Sum

def get_loan_deduction(payee, month, year):
    """
    Fetch loan deduction for a payee for a specific month.
    This is a placeholder for the separate Loan App integration.
    
    Returns:
        Decimal: Amount to deduct.
    """
    # Check if payroll period exists for this month/year
    if not PayrollPeriod.objects.filter(month=month, year=year).exists():
        return Decimal("0.00")
    
    # Get active loan applications for the payee
    payee_loans = LoanApplication.objects.filter(payee=payee)
    
    if not payee_loans.exists():
        return Decimal("0.00")
    
    # Calculate total monthly deduction from all active loans
    total_deduction = payee_loans.aggregate(
        total=Sum('monthly_deduction')
    )['total'] or Decimal("0.00")
    
    # Update loan tenure for each active loan
    for loan in payee_loans:
        loan.tenure_months -= 1
        if loan.tenure_months <= 0:
            loan.active = False
        loan.save()
    
    return total_deduction



def initialize_paystack_transaction(email, amount, reference, callback_url):
    """
    Initialize a transaction with Paystack.
    """
    url = "https://api.paystack.co/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "email": email,
        "amount": int(amount * 100), # Amount in kobo
        "reference": reference,
        "callback_url": callback_url
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"status": False, "message": str(e)}

def create_transfer_recipient(name, account_number, bank_code):
    """
    Create a transfer recipient on Paystack.
    """
    url = "https://api.paystack.co/transferrecipient"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "type": "nuban",
        "name": name,
        "account_number": account_number,
        "bank_code": bank_code,
        "currency": "NGN"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"status": False, "message": str(e)}

