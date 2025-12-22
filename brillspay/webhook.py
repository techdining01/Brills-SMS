import json
import hmac
import hashlib
from django.conf import settings
from django.http import HttpResponse

from brillspay.models import Transaction
from .views import verify_payment


def paystack_webhook(request):
    paystack_signature = request.headers.get("x-paystack-signature")
    body = request.body

    computed_signature = hmac.new(
        settings.PAYSTACK_SECRET_KEY.encode(),
        body,
        hashlib.sha512
    ).hexdigest()

    if computed_signature != paystack_signature:
        return HttpResponse(status=400)

    payload = json.loads(body)

    if payload["event"] == "charge.success":
        reference = payload["data"]["reference"]
        verify_payment(reference)

    return HttpResponse(status=200)
