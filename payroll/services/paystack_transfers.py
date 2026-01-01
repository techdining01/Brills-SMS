import requests
from django.conf import settings


PAYSTACK_URL = "https://api.paystack.co/transfer"


def initiate_transfer(transaction):
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "source": "balance",
        "amount": int(transaction.amount * 100),
        "recipient": {
            "type": "nuban",
            "name": transaction.account_name,
            "account_number": transaction.account_number,
            "bank_code": "XXX",  # resolve bank code earlier
            "currency": "NGN",
        },
    }

    response = requests.post(PAYSTACK_URL, json=payload, headers=headers)
    data = response.json()

    if response.status_code == 200 and data.get("status"):
        transaction.status = "success"
        transaction.paystack_reference = data["data"]["reference"]
    else:
        transaction.status = "failed"
        transaction.failure_reason = str(data)

    transaction.save()
