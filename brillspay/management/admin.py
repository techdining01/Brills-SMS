# brillspay/admin.py
from django.contrib import admin
from .models import Category, Product, Order, OrderItem

# --- 1. Category Admin ---
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

# --- 2. Product Admin (Including Stock) ---
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock_quantity', 'image', 'created_at']
    list_filter =['created_at', 'category']
    list_editable = ['price', 'stock_quantity', 'image']
    search_fields = ['name', 'description']
    
    fieldsets = (
        (None, {'fields': ('name', 'slug', 'category', 'description')}),
        ('Pricing & Stock', {'fields': ('price', 'stock')}),
    )

# --- 3. Order Item Inline for Order Admin ---
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['order']
    readonly_fields = ['price', 'quantity']
    extra = 0
    
   

# --- 4. Order Admin (Tracking Payments) ---
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'payment_verified', 'reference', 'created_at']
    list_filter = ['payment_verified', 'created_at']
    search_fields = ['id', 'user__username', 'reference']
    inlines = [OrderItemInline]
    readonly_fields = ['user', 'reference', 'total_amount']
    
    def total_amount(self, obj):
        return obj.total_amount()
    total_amount.short_description = 'Total Order Cost'