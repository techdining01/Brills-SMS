import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from payroll.models import PaymentTransaction


@csrf_exempt
def paystack_webhook(request):
    payload = json.loads(request.body)
    event = payload.get("event")

    if event == "transfer.success":
        ref = payload["data"]["reference"]
        tx = PaymentTransaction.objects.get(paystack_reference=ref)
        tx.status = "success"
        tx.save()

    elif event == "transfer.failed":
        ref = payload["data"]["reference"]
        tx = PaymentTransaction.objects.get(paystack_reference=ref)
        tx.status = "failed"
        tx.failure_reason = payload["data"]["reason"]
        tx.save()

    return HttpResponse(status=200)
