# Paystack service integration
import requests
from django.conf import settings

PAYSTACK_URL = "https://api.paystack.co/transaction/initialize"


def init_payment(email, amount, reference):
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "email": email,
        "amount": int(amount * 100),
        "reference": reference,
        "callback_url": settings.PAYSTACK_CALLBACK_URL,
    }

    res = requests.post(PAYSTACK_URL, json=payload, headers=headers)
    res.raise_for_status()

    return res.json()["data"]["authorization_url"]
