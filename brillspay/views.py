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

import logging
payment_logger = logging.getLogger('brillspay')


@login_required
@parent_required
def product_list(request):
    products = Product.objects.filter(is_active=True)
    return render(request, 'brillspay/product_list.html', {'products': products})


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
@parent_required
def checkout(request):
    cart = Cart.objects.get(user=request.user)

    if cart.items.count() == 0:
        return redirect('product_list')

    # Create order
    order = Order.objects.create(
        user=request.user,
        total_amount=cart.total()
    )

    # Paystack init
    payload = {
        "email": request.user.email,
        "amount": int(order.total_amount * 100),
        "reference": str(order.reference),
        "callback_url": request.build_absolute_uri('/store/payment/callback/')
    }

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        f"{settings.PAYSTACK_BASE_URL}/transaction/initialize",
        json=payload,
        headers=headers
    )

    res = response.json()

    if res.get("status"):
        return redirect(res["data"]["authorization_url"])
    
    return redirect('view_cart')



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

                payment_logger.info(
                    f"PAYMENT VERIFIED | Ref={reference} | User={order.user_id} | Amount={amount}"
                )
            return JsonResponse({"status": "success"})
        else:
            payment_logger.warning(f"PAYMENT FAILED | Ref={reference}")
            return JsonResponse({"status": "failed"}, status=400)
    except Exception as e:
        payment_logger.error(f"WEBHOOK ERROR | {str(e)}")
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@login_required
@admin_required
def transactions_dashboard(request):
    transactions = PaymentTransaction.objects.select_related('order', 'order__user')
    return render(request, 'admin/transactions.html', {
        'transactions': transactions
    })










# import logging
# logger = logging.getLogger('brillspay')

# logger.info(f"Payment verified: {reference}")


@csrf_exempt
def paystack_webhook(request):
    signature = request.headers.get('x-paystack-signature')
    payload = request.body

    computed = hmac.new(
        key=settings.PAYSTACK_SECRET_KEY.encode(),
        msg=payload,
        digestmod=hashlib.sha512
    ).hexdigest()

    if signature != computed:
        return HttpResponse(status=401)

    event = json.loads(payload)
    data = event['data']

    if event['event'] == 'charge.success':
        reference = data['reference']
        amount = data['amount'] / 100

        transaction, created = PaymentTransaction.objects.get_or_create(
            reference=reference,
            defaults={
                'order': Order.objects.get(paystack_reference=reference),
                'amount': amount,
                'status': data['status'],
                'gateway_response': data,
                'verified': True
            }
        )

        order = transaction.order
        order.status = 'paid'
        order.payment_verified = True
        order.save()    
        
    payment_logger.info(
        f"PAYMENT VERIFIED | Ref={reference} | User={order.user_id} | Amount={amount}"
    )

    payment_logger.warning(
        f"PAYMENT FAILED | Payload={data}"
    )

    return HttpResponse(status=200)
