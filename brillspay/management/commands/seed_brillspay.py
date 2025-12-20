from django.core.management.base import BaseCommand
from django.utils.text import slugify
from decimal import Decimal

from brillspay.models import ProductCategory, Product


class Command(BaseCommand):
    help = "Seed BrillsPay categories and products"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("🌱 Seeding BrillsPay data..."))

        categories = [
            "JSS1", "JSS2", "JSS3",
            "SSS1", "SSS2", "SSS3",
        ]

        products_per_class = [
            {
                "name": "Exam Access Fee",
                "price": Decimal("2500.00"),
                "description": "Unlock access to all examinations for this term."
            },
            {
                "name": "CBT Access Fee",
                "price": Decimal("1500.00"),
                "description": "Computer-Based Test access for this class."
            },
            {
                "name": "Result Checking PIN",
                "price": Decimal("1000.00"),
                "description": "Access and download academic results."
            },
        ]

        # =========================
        # Create Categories
        # =========================
        for cat_name in categories:
            category, created = ProductCategory.objects.get_or_create(
                name=cat_name,
                defaults={"slug": slugify(cat_name)}
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"✅ Category created: {cat_name}"))
            else:
                self.stdout.write(self.style.WARNING(f"⚠️ Category exists: {cat_name}"))

            # =========================
            # Create Products per Category
            # =========================
            for product in products_per_class:
                obj, created = Product.objects.get_or_create(
                    name=product["name"],
                    category=category,
                    defaults={
                        "price": product["price"],
                        "description": product["description"],
                        "is_active": True,
                    }
                )

                if created:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"   ➕ Product added: {product['name']} ({cat_name})"
                        )
                    )

        self.stdout.write(self.style.SUCCESS("🎉 BrillsPay seeding completed successfully!"))
