import requests
from django.conf import settings
from payroll.models import TransferRecipient


def get_or_create_recipient(payee):
    recipient = TransferRecipient.objects.filter(payee=payee).first()
    if recipient:
        return recipient.recipient_code

    bank = payee.bank_accounts.filter(is_primary=True).first()

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
            "bank_code": "XXX",
            "currency": "NGN",
        },
    ).json()

    code = response["data"]["recipient_code"]

    TransferRecipient.objects.create(
        payee=payee,
        recipient_code=code,
        bank_name=bank.bank_name,
        account_number=bank.account_number,
    )

    return code
