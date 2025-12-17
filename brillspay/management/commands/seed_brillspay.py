from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string
from accounts.models import User
from brillspay.models import Product, Order, PaymentTransaction, Category

class Command(BaseCommand):
    help = "Seed ecommerce products, orders, PaymentTransactions"

    def handle(self, *args, **kwargs):
        products = []
        category, _ = Category.objects.get_or_create(name = 'Student-Ware', slug ='student-Ware' )
        for i in range(5):
            p, _ = Product.objects.get_or_create(
                name=f"School Item {i}",
                category=category,
                defaults={
                    "price": 5000 + (i * 1000),
                    "stock_quantity": 20
                }
            )
            products.append(p)

        student = User.objects.filter(role=User.Role.STUDENT).first()

        order = Order.objects.create(
            user=student,
            status="paid",
            total_amount=products[0].price
        )

        PaymentTransaction.objects.create(
            order=order,
            reference=get_random_string(12),
            amount=order.total_amount,
            status="success",
            gateway_response = {
                'success': 'success'
            }
        )

        self.stdout.write(self.style.SUCCESS("BrillsPay seeded successfully"))
