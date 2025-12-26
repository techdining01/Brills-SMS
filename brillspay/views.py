import os
import uuid
import json
import hmac
import hashlib
import logging
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.http import HttpResponse, JsonResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from exams.models import ExamAccess
from .models import Product, Cart, CartItem,  Order, Transaction, PaymentTransaction, OrderItem,  BrillsPayLog
from django.contrib import messages
from django.contrib.auth import get_user_model
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Table, TableStyle, Image
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum
from django.db import connection

from brillspay.utils import get_or_create_cart

User = get_user_model()

payment_logger = logging.getLogger("system")

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




def cart_sidebar(request):
    ward_id = request.GET.get("ward")
    ward = get_object_or_404(User, id=ward_id, role="STUDENT")

    cart = get_or_create_cart(request.user, ward)

    items = cart.items.select_related("product") if cart else []

    return render(request, "brillspay/partials/cart_sidebar.html", {
        "cart": cart,
         "ward": ward,
        "items": items,
        "has_items": bool(items),
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

    if action == "decrease":
        item.quantity -= 1
        if item.quantity <= 0:
            item.delete()
        else:
            item.save()

    if action == "remove":
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
def checkout(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    ward_id = request.POST.get("ward_id")
    try:
        ward = get_object_or_404(User, id=ward_id, role="STUDENT")
    except ValueError as e:
        # Log details to help debug malformed IDs (e.g., UUID parsing errors)
        logger = logging.getLogger("brillspay")
        logger.exception("Failed to resolve ward in checkout; ward_id=%r POST=%r", ward_id, dict(request.POST))
        messages.error(request, "Invalid ward selected. Please re-select ward and try again.")
        return redirect("brillspay:brillspay_products")

    cart = get_object_or_404(
        Cart.objects.prefetch_related("items__product"),
        user=request.user,
        ward=ward
    )

    if not cart.items.exists():
        messages.error(request, "Cart is empty")
        return redirect("brillspay:brillspay_products")

    total = sum(item.product.price * item.quantity for item in cart.items.all())

    # 🔒 Prevent duplicate pending orders
    try:
        order = Order.objects.filter(
            buyer=request.user,
            ward=ward,
            status="PENDING"
        ).first()
    except ValueError as e:
        logger = logging.getLogger("brillspay")
        logger.exception("UUID conversion error while querying Order (likely malformed UUID in DB). ward_id=%r, user=%r, POST=%r",
                         ward_id, request.user.id, dict(request.POST))

        # Inspect raw DB rows to see the offending values (bypass Django field conversion)
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT id, buyer_id, ward_id, status FROM brillspay_order WHERE buyer_id=%s AND ward_id=%s AND status=%s LIMIT 10",
                    [request.user.id, ward.id, "PENDING"],
                )
                raw_rows = cursor.fetchall()
            logger.error("Raw order rows for buyer=%s ward=%s status=PENDING: %s", request.user.id, ward.id, raw_rows)
        except Exception:
            logger.exception("Failed to fetch raw order rows")

        messages.error(request, "A system error occurred while processing your order. Please contact support.")
        return redirect("brillspay:brillspay_products")

    if not order:
        order = Order.objects.create(
            buyer=request.user,
            ward=ward,
            total_amount=total,
            status="PENDING"
        )

        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product_name=item.product.name,
                price=item.product.price,
                quantity=item.quantity
            )

        Transaction.objects.create(
            internal_reference=order.reference,
            user=request.user,
            ward=ward,
            order=order,
            amount=total,
            status="initialized"
        )

        BrillsPayLog.objects.create(
            user=request.user,
            order=order,
            action="ORDER_CREATED",
            message="Order created from cart"
        )

    return redirect("brillspay:checkout_detail", order_id=order.id)



@login_required
def checkout_detail(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        buyer=request.user,
        status="PENDING"
    )

    return render(request, "brillspay/checkout.html", {
        "order": order,
        "transaction": order.transaction
    })



logger = logging.getLogger("brillspay")
def csrf_failure(request, reason=""):
    logger.warning("CSRF failure: reason=%s cookies=%s headers=%s POST=%s",
                   reason, request.COOKIES, {k: request.META.get(k) for k in ['HTTP_REFERER']}, dict(request.POST))
    return HttpResponse("CSRF failure (logged)", status=403)



@login_required
def paystack_initialize(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        buyer=request.user,
        status="PENDING"
    )

    transaction = order.transaction

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    # Generate internal reference if not exists
    if not transaction.internal_reference:
        transaction.internal_reference = f"BP-{uuid.uuid4().hex[:10].upper()}"
        transaction.save()

    payload = {
        "email": request.user.email,
        "amount": int(order.total_amount * 100),
        "callback_url": settings.PAYSTACK_CALLBACK_URL,
        "metadata": {
            "order_id": str(order.id),
            "ward_id": str(order.ward.id),
            "user_id": str(request.user.id),
            "internal_reference": transaction.internal_reference,  # Add internal ref to metadata
        }
    }

    try:
        response = requests.post(
            "https://api.paystack.co/transaction/initialize",
            json=payload,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()

        if not data.get("status"):
            messages.error(request, "Unable to initialize payment.")
            return redirect("brillspay:checkout")

        # Get Paystack's reference
        paystack_ref = data["data"]["reference"]
        
        # Update Transaction with gateway reference
        transaction.gateway_reference = paystack_ref
        transaction.save()
        
        # Create PaymentTransaction record for audit
        PaymentTransaction.objects.create(
            order=order,
            gateway_reference=paystack_ref,
            amount=order.total_amount,
            verified=False,
            raw_response=data
        )

        return redirect(data["data"]["authorization_url"])

    except requests.RequestException as e:
        logger.error(f"Paystack initialization failed: {str(e)}")
        messages.error(request, "Payment service unavailable. Please try again.")
        return redirect("brillspay:checkout")
    


def paystack_callback(request):
    reference = request.GET.get("reference")

    if not reference:
        messages.error(request, "Invalid payment reference")
        return redirect("brillspay:brillspay_products")

    tx = get_object_or_404(Transaction, reference=reference)

    # Do NOT trust browser redirect for verification
    # Webhook will confirm payment later

    if tx.verified:
        messages.success(request, "Payment successful")
    else:
        messages.info(
            request,
            "Payment received. Verification in progress."
        )

    return render(
        request,
        "brillspay/payment_status.html",
        {"transaction": tx}
    )



@login_required
def payment_status_check(request):
    reference = request.GET.get("ref")
    try:
        tx = Transaction.objects.get(internal_reference=reference, user=request.user)
        return JsonResponse({
            "status": tx.status,
            "verified": tx.verified
        })
    except Transaction.DoesNotExist:
        return JsonResponse({"status": "unknown", "verified": False})


import hmac
import hashlib
import json
import requests
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.db import transaction as db_transaction
import logging

logger = logging.getLogger('brillspay')

@csrf_exempt
def paystack_webhook(request):
    """Handle Paystack webhook notifications."""
    
    logger.info(f"Webhook received - Method: {request.method}")
    
    if request.method != "POST":
        return HttpResponse("Method not allowed", status=405)

    try:
        # Get raw body
        body = request.body
        
        # Verify signature
        signature = request.headers.get("X-Paystack-Signature")
        if not signature:
            logger.error("Missing X-Paystack-Signature header")
            return HttpResponse("Missing signature", status=400)

        secret = settings.PAYSTACK_SECRET_KEY.encode('utf-8')
        computed_signature = hmac.new(secret, body, hashlib.sha512).hexdigest()
        
        if not hmac.compare_digest(computed_signature, signature):
            logger.error("Invalid webhook signature")
            return HttpResponse("Invalid signature", status=400)

        # Parse payload
        payload = json.loads(body.decode('utf-8'))
        event = payload.get("event")
        data = payload.get("data", {})
        gateway_reference = data.get("reference")  # Paystack's reference
        
        logger.info(f"Event: {event}, Gateway Ref: {gateway_reference}")

        # Only process successful charges
        if event != "charge.success":
            logger.info(f"Ignoring non-success event: {event}")
            return HttpResponse("OK", status=200)

        if not gateway_reference:
            logger.error("No gateway reference in payload")
            return HttpResponse("No reference", status=200)

        # Use database transaction for atomic operations
        with db_transaction.atomic():
            # Look up the Transaction
            transaction = None
            
            # First try: Find by gateway_reference in Transaction model
            try:
                transaction = Transaction.objects.select_for_update().get(
                    gateway_reference=gateway_reference
                )
                logger.info(f"Found Transaction by gateway_reference: {transaction.id}")
            except Transaction.DoesNotExist:
                # Second try: Find by gateway_reference in PaymentTransaction
                try:
                    payment_tx = PaymentTransaction.objects.select_for_update().get(
                        gateway_reference=gateway_reference
                    )
                    # Link to Transaction if not already linked
                    transaction = payment_tx.order.transaction
                    if transaction and not transaction.gateway_reference:
                        transaction.gateway_reference = gateway_reference
                        transaction.save()
                    logger.info(f"Found via PaymentTransaction: {transaction.id if transaction else 'No transaction linked'}")
                except PaymentTransaction.DoesNotExist:
                    # Third try: Check metadata
                    metadata = data.get("metadata", {})
                    internal_reference = metadata.get("internal_reference")
                    
                    if internal_reference:
                        try:
                            transaction = Transaction.objects.select_for_update().get(
                                internal_reference=internal_reference
                            )
                            # Update with gateway reference
                            transaction.gateway_reference = gateway_reference
                            transaction.save()
                            logger.info(f"Found via metadata (internal_reference): {transaction.id}")
                        except Transaction.DoesNotExist:
                            logger.error(f"Transaction not found with internal_reference: {internal_reference}")
                            return HttpResponse("Transaction not found", status=200)
                    else:
                        logger.error(f"No transaction found for gateway_reference: {gateway_reference}")
                        return HttpResponse("Transaction not found", status=200)

            # If still no transaction, return error
            if not transaction:
                logger.error(f"Could not find transaction for reference: {gateway_reference}")
                return HttpResponse("Transaction not found", status=200)

            # Skip if already verified
            if transaction.verified:
                logger.info(f"Transaction {gateway_reference} already verified")
                return HttpResponse("Already processed", status=200)

            # Verify with Paystack API
            verify_url = f"https://api.paystack.co/transaction/verify/{gateway_reference}"
            headers = {
                "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
                "Content-Type": "application/json"
            }
            
            try:
                verify_response = requests.get(verify_url, headers=headers, timeout=10)
                verify_response.raise_for_status()
                verification_data = verify_response.json()
                
                if not verification_data.get("status"):
                    logger.error(f"Paystack verification failed: {verification_data}")
                    return HttpResponse("Verification failed", status=200)
                    
            except requests.RequestException as e:
                logger.error(f"Paystack API error: {str(e)}")
                return HttpResponse("API verification error", status=200)

            # Update Transaction
            transaction.status = "success"
            transaction.verified = True
            transaction.payload = verification_data.get("data", {})
            transaction.save()
            logger.info(f"Updated Transaction {transaction.id} to verified")

            # Update Order
            order = transaction.order
            order.status = "PAID"
            order.save()
            logger.info(f"Updated Order {order.id} to PAID")

            # Update PaymentTransaction
            try:
                payment_tx = PaymentTransaction.objects.get(gateway_reference=gateway_reference)
                payment_tx.verified = True
                payment_tx.raw_response = verification_data
                payment_tx.save()
                logger.info(f"Updated PaymentTransaction for {gateway_reference}")
            except PaymentTransaction.DoesNotExist:
                # Create PaymentTransaction if it doesn't exist
                PaymentTransaction.objects.create(
                    order=order,
                    gateway_reference=gateway_reference,
                    amount=transaction.amount,
                    verified=True,
                    raw_response=verification_data
                )
                logger.info(f"Created PaymentTransaction for {gateway_reference}")

            # Clear cart
            try:
                CartItem.objects.filter(
                    cart__user=transaction.user,
                    cart__ward=transaction.ward
                ).delete()
                logger.info(f"Cleared cart for user {transaction.user.id}")
            except Exception as e:
                logger.warning(f"Failed to clear cart: {str(e)}")

            # Grant exam access
            try:
                if hasattr(order, 'exam') and order.exam:
                    from exams.models import ExamAccess
                    ExamAccess.objects.get_or_create(
                        student=order.ward,
                        exam=order.exam,
                        defaults={
                            "via_payment": True,
                            "granted_by": transaction.user,
                            "transaction": transaction
                        }
                    )
                    logger.info(f"Granted exam access for ward {order.ward.id}")
            except Exception as e:
                logger.warning(f"Failed to grant exam access: {str(e)}")

            logger.info(f"Successfully processed payment: {gateway_reference}")
            return HttpResponse("Payment verified successfully", status=200)

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in webhook: {str(e)}")
        return HttpResponse("Invalid JSON", status=400)
    except Exception as e:
        logger.error(f"Unexpected error in webhook: {str(e)}", exc_info=True)
        return HttpResponse("Processing error", status=200)
    

@staff_member_required
def webhook_monitor(request):
    txs = Transaction.objects.order_by("-created_at")[:20]
    return render(request, "brillspay/webhook_monitor.html", {
        "transactions": txs
    })




# @login_required
# def checkout(request, ward_id):
#     cart = get_object_or_404(
#         Cart.objects.prefetch_related("items__product"),
#         user=request.user,
#         ward_id=ward_id
#     )

#     if not cart.items.exists():
#         messages.error(request, "Cart is empty")
#         return redirect("brillspay:product_list")

#     # Server-side total (never trust frontend)
#     total = sum(item.product.price * item.quantity for item in cart.items.all())

#     order = Order.objects.create(
#         buyer=request.user,
#         ward=cart.ward,
#         total_amount=total,
#         status="PENDING"
#     )

#     for item in cart.items.all():
#         OrderItem.objects.create(
#             order=order,
#             product_name=item.product.name,
#             price=item.product.price,
#             quantity=item.quantity
#         )

#     # Create pending transaction
#     tx = Transaction.objects.create(
#         reference=f"BP-{uuid.uuid4().hex[:10].upper()}",
#         user=request.user,
#         ward=cart.ward,
#         order=order,
#         amount=total,
#         status="initialized",
#         payload=None
#     )

#     # Clear cart ONLY after order is created
#     cart.items.all().delete()

#     BrillsPayLog.objects.create(
#         user=request.user,
#         order=order,
#         action="ORDER_CREATED",
#         message="Order created from cart",
#         metadata={"transaction": tx.reference}
#     )

#     return redirect("brillspay:paystack_init", tx.reference)



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

    else:
        tx.status = "failed"
        tx.save()

    return JsonResponse({"status": tx.status})



def unlock_cbt_from_order(order):
    """
    Grants CBT access after successful BrillsPay payment.
    """
    for item in order.items.all():
        ExamAccess.objects.get_or_create(
            student=order.ward,
            exam_name=item.product_name, 
            defaults={"via_payment": True}
        )



def handle_successful_transaction(tx: Transaction):
    """
    Finalizes transaction and order.
   """
    if tx.verified and tx.status == "success":
        return  

    tx.verified = True
    tx.status = "success"
    tx.save(update_fields=["verified", "status"])

    order = tx.order
    order.status = "PAID"
    order.save(update_fields=["status"])

    unlock_cbt_from_order(order)


    BrillsPayLog.objects.create(
        user=tx.user,
        order=order,
        action="PAYMENT_SUCCESS",
        message="Payment verified successfully",
        metadata={
            "reference": tx.reference,
            "amount": str(tx.amount)
        }
    )


def admin_override_order(order: Order, admin_user):
    if hasattr(order, "transaction"):
        raise ValueError("Order already has a transaction")

    tx = Transaction.objects.create(
        reference=f"ADMIN-{uuid.uuid4().hex[:10].upper()}",
        user=admin_user,
        ward=order.ward,
        order=order,
        amount=order.total_amount,
        verified=True,
        status="success",
        payload={"source": "admin_override"}
    )

    order.status = "OVERRIDDEN"
    order.is_override = True
    order.save(update_fields=["status", "is_override"])

    BrillsPayLog.objects.create(
        user=admin_user,
        order=order,
        action="ADMIN_OVERRIDE",
        message="Order approved via admin override",
        metadata={"reference": tx.reference}
    )

    handle_successful_transaction(tx)


@login_required
def receipt_view(request, reference):
    tx = get_object_or_404(
        Transaction,
        reference=reference,
        user=request.user
    )

    return render(request, "brillspay/receipt.html", {
        "transaction": tx,
        "order": tx.order,
    })



def unlock_exams_for_order(order, actor):
    """
    Unlocks CBT access after successful payment.
    """
    for item in order.items.all():
        exams = getattr(item, "exams", None)

        if not exams:
            continue

        for exam in exams.all():
            ExamAccess.objects.get_or_create(
                student=order.ward,
                exam=exam,
                defaults={
                    "via_payment": True,
                    "granted_by": actor,
                }
            )




from django.db import transaction as db_transaction

@csrf_exempt
def paystack_webhook(request):
    paystack_signature = request.headers.get("x-paystack-signature")
    raw_body = request.body

    # 1️⃣ Verify signature
    computed_signature = hmac.new(
        key=settings.PAYSTACK_SECRET_KEY.encode(),
        msg=raw_body,
        digestmod=hashlib.sha512
    ).hexdigest()

    if paystack_signature != computed_signature:
        return HttpResponse(status=400)

    payload = json.loads(raw_body)

    if payload.get("event") != "charge.success":
        return HttpResponse(status=200)

    data = payload["data"]
    reference = data["reference"]

    try:
        tx = Transaction.objects.select_related(
            "order", "ward"
        ).get(reference=reference)
    except Transaction.DoesNotExist:
        return HttpResponse(status=200)

    # 2️⃣ Idempotency guard
    if tx.verified:
        return HttpResponse(status=200)

    with db_transaction.atomic():
        # 3️⃣ Verify transaction
        tx.verified = True
        tx.status = "success"
        tx.payload = payload
        tx.save()

        order = tx.order
        order.status = "PAID"
        order.save()

        # 4️⃣ CLEAR CART (SAFE POINT)
        Cart.objects.filter(
            user=tx.user,
            ward=tx.ward
        ).delete()

        # 5️⃣ CBT AUTO-UNLOCK
        unlock_exams_for_order(order, tx.user)

        # 6️⃣ LOG
        BrillsPayLog.objects.create(
            user=tx.user,
            order=order,
            action="PAYMENT_SUCCESS",
            message="Payment verified via Paystack webhook",
            metadata={
                "reference": reference,
                "amount": data["amount"] / 100,
                "channel": data.get("channel"),
            }
        )

    return HttpResponse(status=200)



@staff_member_required
def admin_transaction_dashboard(request):
    qs = Transaction.objects.select_related(
        "user", "ward", "order"
    ).order_by("-created_at")

    status = request.GET.get("status")
    if status:
        qs = qs.filter(status=status)

    total_revenue = qs.filter(
        verified=True,
        status="success"
    ).aggregate(total=Sum("amount"))["total"] or 0

    return render(request, "brillspay/admin/transactions.html", {
        "transactions": qs,
        "total_revenue": total_revenue,
    })


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


# @login_required
# def checkout(request):
#     cart = Cart.objects.filter(user=request.user).first()
#     if not cart or not cart.items.exists():
#         messages.error(request, "Cart is empty")
#         return redirect("brillspay:cart_detail")

#     order = Order.objects.create(
#         buyer=request.user,
#         ward=cart.ward,
#         amount=cart.total_amount
#     )

#     for item in cart.items.all():
#         OrderItem.objects.create(
#             order=order,
#             product=item.product,
#             quantity=item.quantity,
#             price=item.product.price
#         )

#     return redirect("brillspay:paystack_init", order_id=order.id)



# @login_required
# def paystack_init(request, order_id):
#     order = get_object_or_404(Order, id=order_id, buyer=request.user)

#     tx = PaymentTransaction.objects.create(
#         user=request.user,
#         order=order,
#         amount=order.amount,
#         reference=uuid.uuid4().hex
#     )

#     return render(request, "brillspay/paystack.html", {
#         "order": order,
#         "tx": tx,
#         "paystack_key": settings.PAYSTACK_PUBLIC_KEY
#     })



# @login_required
# def verify_payment(request, reference):
#     tx = get_object_or_404(PaymentTransaction, reference=reference)

#     tx.paystack_status = "SUCCESS"
#     tx.save()

#     tx.order.status = "PAID"
#     tx.order.save()

#     # AUTO UNLOCK EXAM / SERVICE
#     for item in tx.order.items.all():
#         if item.product.exam:
#             ExamAccess.objects.get_or_create(
#                 student=tx.order.ward,
#                 exam=item.product.exam,
#                 defaults={"via_payment": True}
#             )

#     Cart.objects.filter(user=request.user).delete()

#     messages.success(request, "Payment successful")
#     return redirect("brillspay:parent_orders")


# @login_required
# def verify_payment(request, reference):
#     tx = get_object_or_404(PaymentTransaction, reference=reference)

#     if tx.paystack_status == "SUCCESS":
#         return redirect("brillspay:receipt_pdf", tx.id)

#     # Normally verify via Paystack API here
#     tx.paystack_status = "SUCCESS"
#     tx.save()

#     order = tx.order
#     order.status = "PAID"
#     order.save()

#     # Unlock services/exams
#     for item in order.items.all():
#         if item.product.exam:
#             ExamAccess.objects.get_or_create(
#                 student=order.ward,
#                 exam=item.product.exam,
#                 defaults={"via_payment": True}
#             )

#     Cart.objects.filter(user=request.user).delete()

#     return redirect("brillspay:receipt_pdf", tx.id)


# @csrf_exempt
# def paystack_webhook(request):
#     payload = request.body
#     signature = request.headers.get("X-Paystack-Signature")

#     computed_signature = hmac.new(
#         settings.PAYSTACK_WEBHOOK_SECRET.encode(),
#         payload,
#         hashlib.sha512
#     ).hexdigest()

#     if signature != computed_signature:
#         return HttpResponse(status=401)

#     event = json.loads(payload)
#     event_type = event.get("event")
#     data = event.get("data")

#     if event_type == "charge.success":
#         reference = data.get("reference")

#         try:
#             tx = PaymentTransaction.objects.select_related("order").get(
#                 reference=reference
#             )
#         except PaymentTransaction.DoesNotExist:
#             return HttpResponse(status=200)

#         if tx.paystack_status == "SUCCESS":
#             return HttpResponse(status=200)

#         tx.paystack_status = "SUCCESS"
#         tx.raw_response = data
#         tx.save()

#         order = tx.order
#         order.status = "PAID"
#         order.save()

#         # 🔓 UNLOCK EXAMS / SERVICES
#         for item in order.items.all():
#             if item.product.exam:
#                 ExamAccess.objects.get_or_create(
#                     student=order.ward,
#                     exam=item.product.exam,
#                     defaults={"via_payment": True}
#                 )

#     return HttpResponse(status=200)


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



