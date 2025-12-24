
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.http import JsonResponse
import uuid
import json
import hmac
import hashlib
import logging
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from exams.models import ExamAccess
from .models import Product, Cart, CartItem,  Order, Transaction, PaymentTransaction, OrderItem
from django.contrib import messages
from django.contrib.auth import get_user_model

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Table, TableStyle, Image
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
import os
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from .models import Cart, CartItem, Product
import json


User = get_user_model()

payment_logger = logging.getLogger("system")

import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from .models import (
    Cart,
    CartItem,
    Product,
    BrillsPayLog
)

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from brillspay.models import Product, CartItem
from brillspay.utils import get_or_create_cart
from accounts.models import User  
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from accounts.models import User


@login_required
def select_ward(request):
    wards = User.objects.filter(
        parents=request.user,
        role="STUDENT"
    )

    if request.method == "POST":
        ward_id = request.POST.get("ward_id")
        return redirect(f"/brillspay/products/?ward={ward_id}")

    return render(request, "brillspay/select_ward.html", {
        "wards": wards
    })



@login_required
def product_list(request):
    """
    Product list filtered by ward's class.
    """
    ward_id = request.GET.get("ward")
    ward = get_object_or_404(User, id=ward_id, role="STUDENT")

    cart = get_or_create_cart(request.user, ward)

    products = Product.objects.filter(
        SchoolClass=ward.student_class,  
        is_active=True
    )

    cart_product_ids = set(
        cart.items.values_list("product_id", flat=True)
    )

    return render(request, "brillspay/product_list.html", {
        "products": products,
        "ward": ward,
        "cart_product_ids": cart_product_ids,
        "cart": cart,
    })


@login_required
@require_POST
def add_to_cart(request):
    product_id = request.POST.get("product_id")
    ward_id = request.POST.get("ward_id")

    ward = get_object_or_404(User, id=ward_id, role="STUDENT")
    product = get_object_or_404(Product, id=product_id, is_active=True)

    # 🔐 HARD RULE: class must match
    if product.SchoolClass != ward.student_class:
        return JsonResponse({"error": "Invalid product for this ward"}, status=403)

    cart = get_or_create_cart(request.user, ward)

    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={"quantity": 1}
    )

    if not created:
        return JsonResponse({
            "status": "exists",
            "message": "Product already in cart",
            "cart_count": cart.items.count()
        })

    # 🧾 LOG
    BrillsPayLog.objects.create(
        user=request.user,
        action="ORDER_CREATED",
        message="Product added to cart",
        metadata={
            "product": product.name,
            "ward": ward.id
        }
    )

    return JsonResponse({
        "status": "added",
        "cart_count": cart.items.count()
    })


@login_required
def cart_view(request, ward_id):
    ward = get_object_or_404(User, id=ward_id, role="STUDENT")
    cart = get_or_create_cart(request.user, ward)

    return render(request, "brillspay/cart.html", {
        "cart": cart,
        "ward": ward
    })



@login_required
def cart_sidebar(request):
    ward_id = request.GET.get("ward")
    ward = get_object_or_404(User, id=ward_id, role="STUDENT")

    cart = get_or_create_cart(request.user, ward)

    return render(request, "brillspay/partials/cart_sidebar.html", {
        "cart": cart,
        "ward": ward
    })


@login_required
def update_cart_item(request):
    item_id = request.POST.get("item_id")
    action = request.POST.get("action") 

    if not item_id or not action:
        return JsonResponse({"success": False}, status=400)


    item = get_object_or_404(CartItem, id=item_id)

    if action == "increase":
        item.quantity += 1
        item.save()

    elif action == "decrease":
        item.quantity -= 1
        if item.quantity <= 0:
            item.delete()
        else:
            item.save()

    elif action == "remove":
        item.delete()

    return JsonResponse({"success": True})


@login_required
def cart_count(request):
    ward_id = request.GET.get("ward")
    ward = get_object_or_404(User, id=ward_id, role="STUDENT")

    cart = get_or_create_cart(request.user, ward)
    count = sum(item.quantity for item in cart.items.all())

    return JsonResponse({"count": count})



@login_required
def verify_payment(request, reference):
    tx = get_object_or_404(Transaction, reference=reference)

    res = requests.get(
        f"https://api.paystack.co/transaction/verify/{reference}",
        headers={"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
    )

    data = res.json()["data"]

    if data["status"] == "success":
        tx.status = "success"
        tx.payload = data
        tx.save()

        # 🔓 future: unlock exams/services here

    else:
        tx.status = "failed"
        tx.save()

    return JsonResponse({"status": tx.status})



@login_required
def store_view(request):
    products = Product.objects.filter(is_active=True, stock_quantity__gt=0)
    wards = request.user.children.filter(role="STUDENT")  # adjust if needed

    return render(request, "brillspay/store.html", {
        "products": products,
        "wards": wards
    })



# @login_required
# def add_to_cart(request):
#     data = json.loads(request.body)
#     product_id = data.get("product_id")
#     ward_id = data.get("ward_id")

#     ward = get_object_or_404(User, id=ward_id, role="STUDENT")
#     product = get_object_or_404(Product, id=product_id)

#     # 🔒 HARD LOCK: class must match
#     if product.school_class.code != ward.student_class.code:
#         return JsonResponse({"error": "Product not allowed for this class"}, status=400)

#     if product.stock_quantity <= 0:
#         return JsonResponse({"error": "Out of stock"}, status=400)

#     cart, _ = Cart.objects.get_or_create(
#         user=request.user,
#         ward=ward
#     )

#     item, created = CartItem.objects.get_or_create(
#         cart=cart,
#         product=product,
#         defaults={"quantity": 1}
#     )

#     if not created:
#         item.quantity += 1
#         item.save(update_fields=["quantity"])

#     return JsonResponse({"success": True})



# @login_required
# def cart_sidebar(request):
#     ward_id = request.GET.get("ward_id")
#     if not ward_id:
#         return HttpResponse("")

#     cart = Cart.objects.filter(
#         user=request.user,
#         ward_id=ward_id
#     ).first()

#     return render(request, "brillspay/cart/sidebar.html", {
#         "cart": cart
#     })



# @login_required
# def cart_detail(request):
#     cart = Cart.objects.filter(
#         user=request.user
#     ).select_related("ward").prefetch_related(
#         "items__product"
#     ).first()

#     return render(request, "brillspay/cart/detail.html", {
#         "cart": cart
#     })



# @login_required
# def update_cart_item(request):
#     if request.method != "POST":
#         return JsonResponse({"error": "Invalid request"}, status=400)

#     item_id = request.POST.get("item_id")
#     action = request.POST.get("action")

#     item = get_object_or_404(
#         CartItem,
#         id=item_id,
#         cart__user=request.user
#     )

#     if action == "increase":
#         item.quantity += 1
#     elif action == "decrease":
#         item.quantity -= 1

#     if item.quantity <= 0:
#         item.delete()
#     else:
#         item.save()

#     cart = item.cart
#     total = sum(i.subtotal for i in cart.items.all())

#     return JsonResponse({
#         "success": True,
#         "item_qty": item.quantity if item.pk else 0,
#         "item_subtotal": item.subtotal if item.pk else 0,
#         "cart_total": total
#     })


# @login_required
# def remove_cart_item(request, item_id):
#     item = get_object_or_404(
#         CartItem,
#         id=item_id,
#         cart__user=request.user
#     )
#     item.delete()

#     return redirect("brillspay:cart_view")


# @login_required
# def clear_cart(request):
#     cart = get_or_create_cart(request.user)
#     cart.items.all().delete()

#     messages.success(request, "Cart cleared")
#     return redirect("brillspay:cart_view")


@login_required
def checkout(request):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart or not cart.items.exists():
        messages.error(request, "Cart is empty")
        return redirect("brillspay:cart_detail")

    order = Order.objects.create(
        buyer=request.user,
        ward=cart.ward,
        amount=cart.total_amount
    )

    for item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price
        )

    return redirect("brillspay:paystack_init", order_id=order.id)



@login_required
def paystack_init(request, order_id):
    order = get_object_or_404(Order, id=order_id, buyer=request.user)

    tx = PaymentTransaction.objects.create(
        user=request.user,
        order=order,
        amount=order.amount,
        reference=uuid.uuid4().hex
    )

    return render(request, "brillspay/paystack.html", {
        "order": order,
        "tx": tx,
        "paystack_key": settings.PAYSTACK_PUBLIC_KEY
    })



@login_required
def verify_payment(request, reference):
    tx = get_object_or_404(PaymentTransaction, reference=reference)

    tx.paystack_status = "SUCCESS"
    tx.save()

    tx.order.status = "PAID"
    tx.order.save()

    # AUTO UNLOCK EXAM / SERVICE
    for item in tx.order.items.all():
        if item.product.exam:
            ExamAccess.objects.get_or_create(
                student=tx.order.ward,
                exam=item.product.exam,
                defaults={"via_payment": True}
            )

    Cart.objects.filter(user=request.user).delete()

    messages.success(request, "Payment successful")
    return redirect("brillspay:parent_orders")


@login_required
def verify_payment(request, reference):
    tx = get_object_or_404(PaymentTransaction, reference=reference)

    if tx.paystack_status == "SUCCESS":
        return redirect("brillspay:receipt_pdf", tx.id)

    # Normally verify via Paystack API here
    tx.paystack_status = "SUCCESS"
    tx.save()

    order = tx.order
    order.status = "PAID"
    order.save()

    # Unlock services/exams
    for item in order.items.all():
        if item.product.exam:
            ExamAccess.objects.get_or_create(
                student=order.ward,
                exam=item.product.exam,
                defaults={"via_payment": True}
            )

    Cart.objects.filter(user=request.user).delete()

    return redirect("brillspay:receipt_pdf", tx.id)


@csrf_exempt
def paystack_webhook(request):
    payload = request.body
    signature = request.headers.get("X-Paystack-Signature")

    computed_signature = hmac.new(
        settings.PAYSTACK_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha512
    ).hexdigest()

    if signature != computed_signature:
        return HttpResponse(status=401)

    event = json.loads(payload)
    event_type = event.get("event")
    data = event.get("data")

    if event_type == "charge.success":
        reference = data.get("reference")

        try:
            tx = PaymentTransaction.objects.select_related("order").get(
                reference=reference
            )
        except PaymentTransaction.DoesNotExist:
            return HttpResponse(status=200)

        if tx.paystack_status == "SUCCESS":
            return HttpResponse(status=200)

        tx.paystack_status = "SUCCESS"
        tx.raw_response = data
        tx.save()

        order = tx.order
        order.status = "PAID"
        order.save()

        # 🔓 UNLOCK EXAMS / SERVICES
        for item in order.items.all():
            if item.product.exam:
                ExamAccess.objects.get_or_create(
                    student=order.ward,
                    exam=item.product.exam,
                    defaults={"via_payment": True}
                )

    return HttpResponse(status=200)


@login_required
def parent_orders(request):
    orders = Order.objects.filter(buyer=request.user)
    return render(request, "brillspay/parent/orders.html", {
        "orders": orders
    })


class WatermarkCanvas(canvas.Canvas):
    def draw_watermark(self):
        self.saveState()
        self.setFont("Helvetica-Bold", 60)
        self.setFillColorRGB(0.85, 0.85, 0.85)
        self.translate(300, 400)
        self.rotate(45)
        self.drawCentredString(0, 0, settings.RECEIPT_WATERMARK)
        self.restoreState()

    def showPage(self):
        self.draw_watermark()
        super().showPage()

    def save(self):
        self.draw_watermark()
        super().save()



@login_required
def payment_receipt_pdf(request, tx_id):
    tx = get_object_or_404(PaymentTransaction, id=tx_id)
    order = tx.order

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="receipt_{tx.reference}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Logo
    if os.path.exists(settings.SCHOOL_LOGO_PATH):
        elements.append(
            Image(
                settings.SCHOOL_LOGO_PATH,
                width=80,
                height=80
            )
        )

    elements.append(Paragraph(
        f"<b>{settings.SCHOOL_NAME}</b>",
        styles["Title"]
    ))

    elements.append(Paragraph(
        "<br/><b>PAYMENT RECEIPT</b><br/><br/>",
        styles["Normal"]
    ))

    elements.append(Paragraph(
        f"<b>Transaction Ref:</b> {tx.reference}<br/>"
        f"<b>Paid By:</b> {tx.user.get_full_name()}<br/>"
        f"<b>Ward:</b> {order.ward.get_full_name()}<br/>"
        f"<b>Date:</b> {tx.created_at.strftime('%d %b %Y %H:%M')}<br/><br/>",
        styles["Normal"]
    ))

    # Items Table
    table_data = [["Item", "Qty", "Unit Price", "Total"]]

    for item in order.items.all():
        table_data.append([
            item.product.name,
            item.quantity,
            f"₦{item.price}",
            f"₦{item.price * item.quantity}"
        ])

    table_data.append([
        "", "", "Grand Total",
        f"₦{order.amount}"
    ])

    table = Table(table_data, colWidths=[200, 60, 100, 100])
    table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 1, colors.black),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("ALIGN", (1,1), (-1,-1), "CENTER"),
        ("FONT", (0,0), (-1,0), "Helvetica-Bold")
    ]))

    elements.append(table)

    elements.append(Paragraph(
        "<br/>Thank you for your payment.<br/>"
        "This receipt is system-generated.",
        styles["Italic"]
    ))

    doc.build(elements, canvasmaker=WatermarkCanvas)
    return response



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



