import json
import hmac
import hashlib
from decimal import Decimal
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from .models import Product, Category, Cart, CartItem, Order, OrderItem

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin

from django.views.decorators.http import require_POST
from django.contrib import messages
from django.urls import reverse
from .models import Product
from .forms import ProductForm 
from django.views.generic import RedirectView
from django.contrib.auth import get_user_model
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


User = get_user_model()

class AdminStaffRequiredMixin(UserPassesTestMixin):
   # --- Permissions Check ---
    def test_func(self):
         return self.request.user.is_authenticated and (self.request.user.role == User.Role.ADMIN or self.request.user.role == User.Role.STAFF)
   

# --- 1. Webhook Listener View ---
@csrf_exempt
def paystack_webhook(request):
    """
    Handles POST requests from Paystack to confirm transactions.
    It is crucial to verify the signature for security.
    """
    
    # 1. Verify Request Signature (SECURITY CHECK)
    signature = request.headers.get('x-paystack-signature')
    
    # Check if the signature header exists
    if not signature:
        return HttpResponse(status=400)

    # Compute the expected hash using HMAC-SHA512
    # The payload is the raw request body bytes
    expected_signature = hmac.new(
        key=bytes(settings.PAYSTACK_SECRET_KEY, 'utf-8'),
        msg=request.body,
        digestmod=hashlib.sha512
    ).hexdigest()

    # Compare the computed hash with the received signature
    if not hmac.compare_digest(expected_signature, signature):
        # Log this failed verification attempt for security monitoring
        print("SECURITY ALERT: Paystack signature verification failed.")
        return HttpResponse(status=400) # Bad Request/Unauthorised

    # 2. Process the Valid Payload
    try:
        event = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return HttpResponse(status=400)

    # We only care about successful transaction events
    if event.get('event') == 'charge.success':
        data = event.get('data')
        reference = data.get('reference')
        
        try:
            # Locate the pending transaction in our database
            transaction = Transaction.objects.get(paystack_reference=reference)
            
            # Update the transaction status and details
            transaction.status = Transaction.Status.SUCCESS
            transaction.paystack_channel = data.get('channel')
            transaction.updated_at = data.get('paid_at') # Use Paystack's paid_at time
            transaction.save()
            
            # TODO: Implement additional logic here:
            # 1. Update Student's fee record (if it was a FEE_PAYMENT)
            # 2. Ship e-commerce order (if it was E_COMMERCE)
            # 3. Trigger Staff salary payment if needed (complex, we'll outline this later)
            
            return JsonResponse({'status': 'success'}, status=200)

        except Transaction.DoesNotExist:
            # This is normal if a transaction was initiated but never recorded locally
            # or if the webhook is for an unknown reference.
            return JsonResponse({'status': 'reference not found'}, status=404)

    # Acknowledge the webhook even if we don't handle the event type
    return HttpResponse(status=200)



# --- 1. Store View ---
@login_required
def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
        
    return render(request, 'brillspay/list.html', {
        'category': category,
        'categories': categories,
        'products': products
    })

# --- 2. Cart Manipulation (Add) ---
@require_POST
@login_required
def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    # Get or create the user's cart
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Get or create the cart item
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'price': product.price} # Capture price at time of adding
    )
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
        
    # Redirect to the cart view (which we'll implement next)
    return redirect('brillspay:cart_detail')

# --- 3. Cart Detail View ---
@login_required
def cart_detail(request):
    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        cart = None
    
    return render(request, 'brillspay/cart_detail.html', {'cart': cart})

# --- 4. Checkout and Payment Initialization ---
@login_required
@transaction.atomic
def checkout_create(request):
    cart = get_object_or_404(Cart, user=request.user)
    if not cart.items.exists():
        # Handle empty cart error
        return redirect('brillspay:cart_detail')

    # 1. Create the Order
    order = Order.objects.create(
        user=request.user,
        full_name=f"{request.user.first_name} {request.user.last_name}",
        email=request.user.email,
        address=request.user.address or "N/A" # Use address from User model
    )
    
    # 2. Transfer Cart Items to Order Items
    for item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product=item.product,
            price=item.price, # Use the price captured in the cart
            quantity=item.quantity
        )
        # Update product stock
        item.product.stock -= item.quantity
        item.product.save()

    # 3. Clear the Cart
    cart.items.all().delete()
    
    # 4. Initialize Paystack Transaction (MOCK)
    total_amount_kobo = int(order.get_total_cost() * Decimal(100))
    # NOTE: The actual Paystack API call goes here.
    
    # --- MOCK PAYSTACK REDIRECT ---
    # In a real scenario, you would get a payment URL from Paystack.
    mock_paystack_url = f"/brillspay/payment/verify/{order.id}/" 
    
    return redirect(mock_paystack_url)


class ProductChangeListRedirectView(AdminStaffRequiredMixin, RedirectView):
    """Redirects to the Django Admin Change List for Products."""
    # This uses the default Django Admin URL name convention: app_label_model_changelist
    permanent = False
    query_string = True
    pattern_name = 'brillspay:manage_products' 

# --- Permissions Check ---
def is_admin_or_staff(user):
    return user.is_authenticated and (user.role == 'ADMIN' or user.role == 'STAFF')

# --- Product Management Views (CRUD) ---

@login_required
@user_passes_test(is_admin_or_staff)
def admin_product_list(request):
    """Admin view to list all products."""
    products = Product.objects.all().order_by('name')
    context = {
        'products': products,
    }
    return render(request, 'brillspay/admin_product_list.html', context)

@login_required
@user_passes_test(is_admin_or_staff)
def admin_product_create(request):
    """Admin view to create a new product."""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, f"Product '{form.cleaned_data['name']}' created successfully.")
            return redirect('brillspay:admin_product_list')
    else:
        form = ProductForm()
        
    context = {'form': form, 'title': 'Create New Product'}
    return render(request, 'brillspay/admin_product_form.html', context)

@login_required
@user_passes_test(is_admin_or_staff)
def admin_product_update(request, pk):
    """Admin view to update an existing product."""
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f"Product '{product.name}' updated successfully.")
            return redirect('brillspay:admin_product_list')
    else:
        form = ProductForm(instance=product)
        
    context = {'form': form, 'title': f'Edit Product: {product.name}'}
    return render(request, 'brillspay/admin_product_form.html', context)

@login_required
@user_passes_test(is_admin_or_staff)
def admin_product_delete(request, pk):
    """Admin view to delete a product."""
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        product.delete()
        messages.success(request, f"Product '{product.name}' deleted.")
        return redirect('brillspay:admin_product_list')

    # Confirmation page for GET request
    context = {'product': product}
    return render(request, 'brillspay/admin_product_confirm_delete.html', context)


class BillingPaymentView(LoginRequiredMixin, TemplateView):
    template_name = 'feature_placeholders/billing_payments.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Billing & Payments"
        # Logic to fetch fees, recent transactions, etc., would go here
        return context
