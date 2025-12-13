from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from decimal import Decimal
import uuid 


User = get_user_model()

class Transaction(models.Model):
    # Transaction Types
    class Type(models.TextChoices):
        FEE_PAYMENT = 'FEE', _('Fee Payment')
        E_COMMERCE = 'ECOMM', _('E-Commerce Purchase')
        SALARY = 'SALARY', _('Staff Salary Payment') # Outgoing payment

    # Status of the transaction
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')           # Waiting for Paystack confirmation
        SUCCESS = 'SUCCESS', _('Success')           # Confirmed by Paystack Webhook
        FAILED = 'FAILED', _('Failed')             # Failed transaction
        REVERSED = 'REVERSED', _('Reversed')       # Payment was later reversed

    # Core fields
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    transaction_type = models.CharField(max_length=50, choices=Type.choices)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Paystack Reference Fields
    paystack_reference = models.CharField(max_length=100, unique=True, db_index=True)
    paystack_channel = models.CharField(max_length=50, blank=True, null=True) # card, bank_transfer, etc.

    # Status and timestamps
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Optional: Foreign key to a specific order/fee item (for future expansion)
    # e.g., order = models.ForeignKey('ECommerceOrder', ...)

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.user.username} - {self.amount} - {self.status}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Transactions"




# --- 1. Product Management ---
class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255)
    
    class Meta:
        verbose_name_plural = 'Categories'
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField(default=0, help_text="Current quantity in stock.")
    image = models.ImageField(upload_to='product/')
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ('name',)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.name

# --- 2. Shopping Cart ---
class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='cart', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    
    class Meta:
        unique_together = ('cart', 'product')
        
    def get_cost(self):
        return self.price * self.quantity

# --- 3. Order & Payment (Paystack Integration Focus) ---
class Order(models.Model):
    # This field links the order to the user who placed it
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='orders', on_delete=models.CASCADE)
    
    # Customer details (can be pre-filled from user profile)
    full_name = models.CharField(max_length=250)
    email = models.EmailField(max_length=250)
    address = models.CharField(max_length=250)
    
    # Order status
    paid = models.BooleanField(default=False)
    
    # Paystack Reference (used to verify payment)
    paystack_ref = models.CharField(max_length=100, blank=True)
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ('-created_at',)
        
    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())
    
    def __str__(self):
        return f'Order {self.id} by {self.user.username}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    
    def get_cost(self):
        return self.price * self.quantity
    

