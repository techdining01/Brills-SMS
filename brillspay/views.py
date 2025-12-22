
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

from brillspay.models import Product, Cart, CartItem




User = get_user_model()


payment_logger = logging.getLogger("system")



@login_required
def get_or_create_cart(request):
    ward_id = request.GET.get("ward_id")

    if not ward_id:
        return JsonResponse(
            {"success": False, "message": "Ward is required"},
            status=400
        )

    ward = get_object_or_404(
        User,
        id=ward_id,
        role="STUDENT"
    )

    cart, created = Cart.objects.get_or_create(
        user=request.user,
        ward=ward
    )

    return JsonResponse({
        "success": True,
        "created": created,
        "cart_id": cart.id,
        "total_items": cart.total_items(),
        "total_amount": float(cart.total_amount()),
    })


from brillspay.models import Cart

def get_or_create_cart_for_user(user, ward):
    cart, created = Cart.objects.get_or_create(
        user=user,
        ward=ward
    )
    return cart



@login_required
def cart_view(request):
    ward_id = request.GET.get("ward_id")


    if not ward_id:
        return redirect("brillspay:products_list")


    ward = get_object_or_404(
        User,
        id=ward_id,
        role="STUDENT"
    )

    cart = get_or_create_cart_for_user(
        user=request.user,
        ward=ward
    )

    return render(request, "brillspay/cart/cart.html", {
        "cart": cart,
        "items": cart.items.select_related("product"),
        "ward": ward,
    })




@login_required
def products_list(request):
    products = Product.objects.filter(is_active=True)

    # Parents see products based on selected ward
    wards = User.objects.filter(parents=request.user, role="STUDENT")


    class_filter = request.GET.get("class")
    if class_filter:
        products = products.filter(school_class=class_filter)


    return render(request, "brillspay/products/list.html", {
        "products": products,
        "wards": wards
    })



# @login_required
# def cart_view(request):
#     cart = get_or_create_cart(request.user)

#     items = cart.items.select_related("product")

#     total = sum(item.subtotal for item in items)

#     return render(
#         request,
#         "brillspay/cart/cart.html",
#         {
#             "cart": cart,
#             "items": items,
#             "total": total
#         }
#     )



@login_required
def store(request):
    user = request.user

    wards = None
    products = Product.objects.none()

    # Parent: show products based on wards' classes
    if user.role == "PARENT":
        wards = user.children.select_related('student_class')

        ward_classes = [
            ward.student_class.id
            for ward in wards
            if ward.student_class
        ]

        products = Product.objects.filter(
            category__in=ward_classes,
            is_active=True
        )

    # Staff/Admin: see all products
    elif user.role in ["STAFF", "ADMIN"]:
        products = Product.objects.filter(is_active=True)

    # Cart count (total cart items, not carts)
    cart_count = Cart.objects.filter(user=user).count()

    return render(request, "brillspay/store.html", {
        "products": products,
        "cart_count": cart_count,
        "wards": wards,  
    })



# @login_required
# def add_to_cart(request, product_id):
#     if request.method != "POST":
#         return redirect("brillspay:product_list")

#     product = get_object_or_404(Product, id=product_id, is_active=True)

#     ward_id = request.POST.get("ward_id")
#     if not ward_id:
#         messages.error(request, "Please select a student")
#         return redirect("brillspay:product_list")

#     ward = get_object_or_404(
#         User,
#         id=ward_id,
#         role="STUDENT",
#         parents=request.user
#     )

#     if product.stock_quantity <= 0:
#         messages.error(request, "Product out of stock")
#         return redirect("brillspay:product_list")

#     cart, _ = Cart.objects.get_or_create(
#         user=request.user,
#         ward=ward
#     )

#     item, created = CartItem.objects.get_or_create(
#         cart=cart,
#         product=product
#     )

#     if not created:
#         item.quantity += 1
#     item.save()

#     messages.success(request, "Item added to cart")
#     return redirect("brillspay:cart_detail")



# @login_required
# def add_to_cart(request):
#     if request.method != "POST":
#         return JsonResponse({"error": "Invalid request"}, status=400)

#     product_id = request.POST.get("product_id")
#     ward_id = request.POST.get("ward_id")

#     product = get_object_or_404(Product, id=product_id)

#     # 🔐 FINAL SAFETY CHECK (DO NOT MOVE THIS)
#     if product.stock_quantity <= 0:
#         return JsonResponse(
#             {"success": False, "message": "Out of stock"},
#             status=400
#         )

#     cart, _ = Cart.objects.get_or_create(
#         user=request.user,
#         ward_id=ward_id,
#         is_checked_out=False
#     )

#     item, created = CartItem.objects.get_or_create(
#         cart=cart,
#         product=product,
#         defaults={"quantity": 1}
#     )

#     if not created:
#         # 🛑 Prevent exceeding available stock
#         if item.quantity + 1 > product.stock_quantity:
#             return JsonResponse(
#                 {"success": False, "message": "Insufficient stock"},
#                 status=400
#             )

#         item.quantity += 1
#         item.save(update_fields=["quantity"])

#     return JsonResponse({
#         "success": True,
#         "cart_total_items": cart.items.count()
#     })




@login_required
def add_to_cart(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    data = json.loads(request.body)
    product_id = data.get("product_id")

    product = get_object_or_404(Product, id=product_id)

    # FINAL SAFETY CHECK
    if product.stock_quantity <= 0:
        return JsonResponse({"error": "Out of stock"}, status=400)

    cart = get_or_create_cart(request.user)

    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={"quantity": 1}
    )

    if not created:
        if item.quantity + 1 > product.stock_quantity:
            return JsonResponse({"error": "Stock limit reached"}, status=400)
        item.quantity += 1
        item.save(update_fields=["quantity"])

    return JsonResponse({
        "success": True,
        "cart_total": cart.total_items()
    })




@login_required
def cart_detail(request):
    cart = Cart.objects.filter(
        user=request.user
    ).select_related("ward").prefetch_related(
        "items__product"
    ).first()

    return render(request, "brillspay/cart/detail.html", {
        "cart": cart
    })


@login_required
def clear_cart(request):
    cart = get_or_create_cart(request.user)
    cart.items.all().delete()

    messages.success(request, "Cart cleared")
    return redirect("brillspay:cart_view")


@login_required
def update_cart_item(request, item_id):
    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user
    )

    qty = int(request.POST.get("quantity", 1))
    if qty < 1:
        item.delete()
    else:
        item.quantity = qty
        item.save()

    return redirect("brillspay:cart_detail")



@login_required
def remove_cart_item(request, item_id):
    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user
    )
    item.delete()
    messages.success(request, "Item removed")
    return redirect("brillspay:cart_detail")


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



