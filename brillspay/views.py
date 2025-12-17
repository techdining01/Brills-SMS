from django.http import JsonResponse
from django.shortcuts import render
from .models import Product
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import JsonResponse
from decimal import Decimal
from .models import Order, Transaction
from .services.paystack import init_payment
import uuid
import json
import hmac
import hashlib
import logging
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Transaction
from exams.models import ExamAccess


payment_logger = logging.getLogger("system")


def _get_cart(request):
    return request.session.setdefault("cart", {"items": {}})

def add_to_cart(request):
    product_id = str(request.POST.get("product_id"))
    product = Product.objects.get(id=product_id)

    cart = _get_cart(request)

    cart["items"][product_id] = {
        "name": product.name,
        "price": str(product.price),
        "qty": 1,
        "class_level": product.class_level
    }

    request.session.modified = True

    return JsonResponse({
        "count": len(cart["items"]),
        "message": "Added to cart"
    })


def remove_from_cart(request):
    product_id = str(request.POST.get("product_id"))
    cart = _get_cart(request)

    cart["items"].pop(product_id, None)
    request.session.modified = True

    return JsonResponse({"count": len(cart["items"])})


def cart_view(request):
    cart = _get_cart(request)
    total = sum(
        Decimal(item["price"]) * item["qty"]
        for item in cart["items"].values()
    )
    return render(request, "brillspay/cart.html", {
        "cart": cart,
        "total": total
    })





@login_required
def checkout_view(request):
    cart = request.session.get("cart", {})
    if not cart.get("items"):
        return redirect("brillspay:store")

    wards = request.user.children.all() if hasattr(request.user, "children") else []

    total = sum(
        Decimal(item["price"]) * item["qty"]
        for item in cart["items"].values()
    )

    if request.method == "POST":
        ward_id = request.POST.get("ward")
        if not ward_id:
            return JsonResponse({"error": "Ward selection required"}, status=400)

        order = Order.objects.create(
            user=request.user,
            ward_id=ward_id,
            total_amount=total
        )

        tx = Transaction.objects.create(
            order=order,
            reference=str(uuid.uuid4()),
            amount=total
        )

        payment_url = init_payment(
            email=request.user.email,
            amount=total,
            reference=tx.reference
        )

        return JsonResponse({"payment_url": payment_url})

    return render(request, "brillspay/checkout.html", {
        "total": total,
        "wards": wards
    })


import requests

@login_required
def payment_callback(request):
    reference = request.GET.get("reference")

    tx = Transaction.objects.get(reference=reference)

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"
    }

    res = requests.get(
        f"https://api.paystack.co/transaction/verify/{reference}",
        headers=headers
    )

    data = res.json()["data"]
    tx.raw_response = data
    tx.verified = data["status"] == "success"
    tx.save()

    if tx.verified:
        tx.order.status = "PAID"
        tx.order.save()

        request.session.pop("cart", None)

    return redirect("brillspay:payment_success")


@csrf_exempt
def paystack_webhook(request):
    signature = request.headers.get("X-Paystack-Signature")
    body = request.body

    expected = hmac.new(
        settings.PAYSTACK_SECRET_KEY.encode(),
        body,
        hashlib.sha512
    ).hexdigest()

    if signature != expected:
        payment_logger.warning("INVALID WEBHOOK SIGNATURE")
        return HttpResponse(status=400)

    payload = json.loads(body)
    event = payload.get("event")
    data = payload.get("data", {})

    if event == "charge.success":
        reference = data["reference"]

        tx = Transaction.objects.select_related(
            "order", "order__ward", "order__exam"
        ).get(reference=reference)

        if tx.verified:
            return HttpResponse(status=200)

        tx.verified = True
        tx.raw_response = data
        tx.save()

        order = tx.order
        order.status = "PAID"
        order.save()

        # 🔓 AUTO UNLOCK EXAM AFTER PAYMENT
        ExamAccess.objects.get_or_create(
            student=order.ward,
            exam=order.exam,
            defaults={"via_payment": True}
        )

        payment_logger.info(f"Order {order.id} marked as PAID via webhook.")
        
    return HttpResponse(status=200)



