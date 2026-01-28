import requests
from django.conf import settings
from django.core.cache import cache
from payroll.models import TransferRecipient


def get_bank_code(bank_name):
    """
    Fetch list of banks from Paystack and find the code for the given bank name.
    """
    # Try to get from cache first (cache for 24 hours)
    banks = cache.get("paystack_banks")

    if not banks:
        try:
            response = requests.get(
                "https://api.paystack.co/bank",
                headers={
                    "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
                }
            )
            if response.status_code == 200:
                banks = response.json()["data"]
                cache.set("paystack_banks", banks, 60 * 60 * 24)
            else:
                raise ValueError(f"Could not fetch banks from Paystack: {response.text}")
        except Exception as e:
            # Fallback or re-raise
            raise ValueError(f"Error connecting to Paystack: {str(e)}")

    # Normalize names for comparison
    target_name = bank_name.lower().strip()
    
    # Common mappings for mismatches
    MAPPINGS = {
        "gtb": "guaranty trust bank",
        "gt bank": "guaranty trust bank",
        "uba": "united bank for africa",
        "first bank": "first bank of nigeria",
        "zenith": "zenith bank",
        "access": "access bank",
        "access (diamond)": "access bank",
    }
    
    target_name = MAPPINGS.get(target_name, target_name)
    
    for bank in banks:
        if bank["name"].lower() == target_name or bank.get("slug", "").replace("-", " ") == target_name:
            return bank["code"]
            
    # Fuzzy match or partial match could be added here, 
    # but for now let's be strict to avoid sending money to wrong bank
    
    # Second pass: check if target name is contained in bank name
    for bank in banks:
        if target_name in bank["name"].lower():
            return bank["code"]

    raise ValueError(f"Could not resolve bank code for '{bank_name}'")


def get_or_create_recipient(payee):
    recipient = TransferRecipient.objects.filter(payee=payee).first()
    if recipient:
        return recipient.recipient_code

    bank = payee.bank_accounts.filter(is_primary=True).first()
    if not bank:
        raise ValueError(f"No primary bank account found for {payee}")

    bank_code = get_bank_code(bank.bank_name)

    response = requests.post(
        "https://api.paystack.co/transferrecipient",
        headers={
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "type": "nuban",
            "name": bank.account_name,
            "account_number": bank.account_number,
            "bank_code": bank_code,
            "currency": "NGN",
        },
    )
    
    data = response.json()
    
    if not data.get("status"):
        raise ValueError(f"Paystack Error: {data.get('message')}")

    code = data["data"]["recipient_code"]

    TransferRecipient.objects.create(
        payee=payee,
        recipient_code=code,
        bank_name=bank.bank_name,
        account_number=bank.account_number,
    )

    return code
