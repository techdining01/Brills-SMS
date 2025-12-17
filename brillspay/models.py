
from django.db import models
from django.conf import settings

import uuid
from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


User = settings.AUTH_USER_MODEL

import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone

User = settings.AUTH_USER_MODEL


class ProductCategory(models.Model):
    """
    Class-based category (e.g. JSS1, SSS3).
    Used to restrict products to student class.
    """
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    School ecommerce product.
    Examples: Exam access, CBT unlock, Result checking, Uniform, etc.
    """

    PRODUCT_TYPES = [
        ("EXAM", "Exam / CBT"),
        ("SERVICE", "School Service"),
        ("MATERIAL", "Material"),
        ("OTHER", "Other"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=255)
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.PROTECT,
        related_name="products"
    )

    product_type = models.CharField(
        max_length=20, choices=PRODUCT_TYPES
    )

    price = models.DecimalField(max_digits=10, decimal_places=2)

    image = models.ImageField(
        upload_to="brillspay/products/",
        blank=True,
        null=True
    )

    description = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.category})"


class Cart(models.Model):
    """
    One active cart per user.
    """
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="cart"
    )

    updated_at = models.DateTimeField(auto_now=True)

    def total_amount(self):
        return sum(item.subtotal() for item in self.items.all())

    def __str__(self):
        return f"Cart - {self.user}"



class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name="items"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("cart", "product")

    def subtotal(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    


class Order(models.Model):
    """
    A finalized purchase.
    EXACTLY ONE ward (student) per order – enforced.
    """

    ORDER_STATUS = [
        ("PENDING", "Pending"),
        ("PAID", "Paid"),
        ("FAILED", "Failed"),
        ("FULFILLED", "Fulfilled"),
        ("OVERRIDDEN", "Admin Override"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    buyer = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="orders"
    )

    ward = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="ward_orders",
        help_text="The student this purchase is for"
    )

    reference = models.CharField(
        max_length=50, unique=True, editable=False
    )

    status = models.CharField(
        max_length=20, choices=ORDER_STATUS, default="PENDING"
    )

    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2
    )

    is_override = models.BooleanField(
        default=False,
        help_text="Admin manually approved this order"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"BP-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reference} - {self.status}"



class OrderItem(models.Model):
    """
    Snapshot of purchased items.
    """
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items"
    )
    product_name = models.CharField(max_length=255)
    product_type = models.CharField(max_length=50)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.unit_price * self.quantity


class PaymentTransaction(models.Model):
    """
    Stores EVERY Paystack interaction.
    Webhook-safe, audit-safe.
    """

    STATUS = [
        ("INITIATED", "Initiated"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
    ]

    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name="transaction"
    )

    reference = models.CharField(max_length=100, unique=True)

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    paystack_status = models.CharField(
        max_length=20, choices=STATUS
    )

    raw_response = models.JSONField(
        help_text="Full Paystack response payload"
    )

    verified_at = models.DateTimeField(
        null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reference} - {self.paystack_status}"



class BrillsPayLog(models.Model):
    """
    Logs everything: payments, overrides, failures, audits.
    """

    ACTIONS = [
        ("PAYMENT_INIT", "Payment Initialized"),
        ("PAYMENT_SUCCESS", "Payment Success"),
        ("PAYMENT_FAILED", "Payment Failed"),
        ("ADMIN_OVERRIDE", "Admin Override"),
        ("ORDER_CREATED", "Order Created"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    order = models.ForeignKey(
        Order, on_delete=models.SET_NULL, null=True, blank=True
    )

    action = models.CharField(max_length=50, choices=ACTIONS)

    message = models.TextField()

    metadata = models.JSONField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} @ {self.created_at}"



class Order(models.Model):
    STATUS = (
        ("PENDING", "Pending"),
        ("PAID", "Paid"),
        ("FAILED", "Failed"),
        ("OVERRIDDEN", "Overridden"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ward = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="ward_orders",
        limit_choices_to={"role": "STUDENT"},
    )

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=15, choices=STATUS, default="PENDING")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id} - {self.status}"


class Transaction(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    reference = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    verified = models.BooleanField(default=False)
    raw_response = models.JSONField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.reference


