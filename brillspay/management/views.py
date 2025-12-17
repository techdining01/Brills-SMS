from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from .models import Cart, Order, PaymentTransaction, Product, Cart, CartItem
from .decorators import parent_required, admin_required
import hmac, hashlib, json
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import requests
from exams.models import Exam
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from .models import Cart, CartItem, Product, Order, OrderItem
import uuid



import logging
logger = logging.getLogger("system")


def product_list(request):
    products = Product.objects.filter(is_active=True)
    cart_count = CartItem.objects.filter(
        cart__user=request.user
    ).count() if request.user.is_authenticated else 0

    return render(request, "brillspay/product_list.html", {
        "products": products,
        "cart_count": cart_count,
    })


@login_required
@parent_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    return render(request, 'brillspay/product_detail.html', {'product': product})


@login_required
@parent_required
def add_to_cart(request):
    product_id = request.POST.get('product_id')
    product = get_object_or_404(Product, id=product_id)

    cart, _ = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        item.quantity += 1
    item.save()

    return JsonResponse({
        'success': True,
        'cart_total': cart.total(),
        'items': cart.items.count()
    })



@login_required
@parent_required
def view_cart(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    return render(request, 'brillspay/cart.html', {'cart': cart})



@login_required
def checkout_view(request):
    cart = Cart.objects.filter(
        user=request.user,
        is_paid=False
    ).prefetch_related("items__product").first()

    if not cart or cart.items.count() == 0:
        messages.warning(request, "Your cart is empty")
        return redirect("brillspay:product_list")

    context = {
        "cart": cart,
        "paystack_public_key": settings.PAYSTACK_PUBLIC_KEY,
    }
    return render(request, "brillspay/checkout.html", context)


@login_required
def init_paystack_payment(request):
    cart = get_object_or_404(
        Cart,
        user=request.user,
        is_paid=False
    )

    reference = f"BRILLS-{uuid.uuid4().hex[:10].upper()}"

    order = Order.objects.create(
        user=request.user,
        reference=reference,
        amount=cart.subtotal,
        status="PENDING",
    )

    for item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price,
        )

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "email": request.user.email,
        "amount": order.amount * 100,
        "reference": order.reference,
        "callback_url": request.build_absolute_uri(
            "/brillspay/payment/callback/"
        ),
        "metadata": {
            "order_id": order.id,
            "user_id": request.user.id
        }
    }

    response = requests.post(
        "https://api.paystack.co/transaction/initialize",
        json=payload,
        headers=headers
    ).json()

    if not response.get("status"):
        messages.error(request, "Unable to initialize payment")
        return redirect("brillspay:checkout")

    return redirect(response["data"]["authorization_url"])


@require_POST
@login_required
def update_cart(request):
    product_id = request.POST.get("product_id")
    action = request.POST.get("action")  # increase | decrease

    cart, _ = Cart.objects.get_or_create(user=request.user, is_paid=False)
    product = get_object_or_404(Product, id=product_id)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if action == "increase":
        cart_item.quantity += 1
        cart_item.save()

    elif action == "decrease":
        cart_item.quantity -= 1
        if cart_item.quantity <= 0:
            cart_item.delete()
        else:
            cart_item.save()

    cart.refresh_totals()

    return JsonResponse({
        "success": True,
        "cart_count": cart.total_items(),
        "cart_total": cart.subtotal,
    })


@require_POST
@login_required
def remove_from_cart(request):
    product_id = request.POST.get("product_id")

    cart = get_object_or_404(Cart, user=request.user, is_paid=False)
    item = get_object_or_404(CartItem, cart=cart, product_id=product_id)

    item.delete()
    cart.refresh_totals()

    return JsonResponse({
        "success": True,
        "cart_count": cart.total_items(),
        "cart_total": cart.subtotal,
    })




@login_required
def exam_checkout(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)

    order, created = Order.objects.get_or_create(
        user=request.user,
        exam=exam,
        defaults={"total": exam.price}
    )

    return render(request, "brillspay/exam_checkout.html", {
        "exam": exam,
        "order": order,
        "paystack_key": settings.PAYSTACK_PUBLIC_KEY
    })


@csrf_exempt
def paystack_webhook(request):
    """
    Paystack webhook callback for verifying payment
    """
    if request.method != "POST":
        return HttpResponse(status=405)

    try:
        event = json.loads(request.body)
        reference = event.get("data", {}).get("reference")
        amount = event.get("data", {}).get("amount") / 100  # Paystack sends kobo

        # Verify with Paystack API
        headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
        r = requests.get(f"https://api.paystack.co/transaction/verify/{reference}", headers=headers)
        result = r.json()

        if result["status"] and result["data"]["status"] == "success":
            # Update order/payment record
            order = PaymentTransaction.objects.filter(reference=reference).first()
            if order:
                order.status = "PAID"
                order.amount_paid = amount
                order.paid_at = result["data"]["paid_at"]
                order.save()

                logger.info(
                    f"PAYMENT VERIFIED | Ref={reference} | User={order.user_id} | Amount={amount}"
                )
            return JsonResponse({"status": "success"})
        else:
            logger.warning(f"PAYMENT FAILED | Ref={reference}")
            return JsonResponse({"status": "failed"}, status=400)
    except Exception as e:
        logger.error(f"WEBHOOK ERROR | {str(e)}")
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@login_required
@admin_required
def transactions_dashboard(request):
    transactions = PaymentTransaction.objects.select_related('order', 'order__user')
    return render(request, 'brillspay/admin/transactions.html', {
        'transactions': transactions
    })


@staff_member_required
def admin_orders(request):
    orders = Order.objects.select_related("user").prefetch_related("items")

    return render(request, "brillspay/admin/orders/list.html", {
        "orders": orders
    })


@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, "brillspay/admin/orders/detail.html", {
    "order": order,

    })


    

@staff_member_required
def admin_update_stock(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        qty = int(request.POST.get("quantity", 0))
        product.stock += qty
        product.save(update_fields=["stock"])

        messages.success(request, "Stock updated successfully")
        return redirect("brillspay:admin_orders")

    return render(request, "brillspay/admin/products/update_stock.html", {
        "product": product
    })


