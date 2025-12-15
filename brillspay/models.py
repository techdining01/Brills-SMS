from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid

User = settings.AUTH_USER_MODEL


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name
    
class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    stock_quantity = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)

    def total(self):
        return sum(item.subtotal() for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.product.price * self.quantity


class Order(models.Model):
    STATUS = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reference = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    payment_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} - {self.reference}"
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product_name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()


class PaymentTransaction(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='transactions')
    reference = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=30)
    gateway_response = models.JSONField()
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    

# class Product(models.Model):
#     category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
#     name = models.CharField(max_length=200)
#     description = models.TextField(blank=True)
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     image = models.ImageField(upload_to='products/', blank=True)
#     is_active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.name


# class Cart(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def total_price(self):
#         return sum(item.subtotal() for item in self.items.all())




# class CartItem(models.Model):
#     cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     quantity = models.PositiveIntegerField(default=1)

#     def subtotal(self):
#         return self.product.price * self.quantity



# class Order(models.Model):
#     STATUS = (
#         ('pending', 'Pending'),
#         ('paid', 'Paid'),
#         ('cancelled', 'Cancelled'),
#     )

#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     total = models.DecimalField(max_digits=10, decimal_places=2)
#     paystack_reference = models.CharField(max_length=100, blank=True, null=True)
#     payment_verified = models.BooleanField(default=False)
#     status = models.CharField(max_length=20, choices=STATUS, default='pending')
#     created_at = models.DateTimeField(default=timezone.now)

#     def __str__(self):
#         return f"Order #{self.id}"



