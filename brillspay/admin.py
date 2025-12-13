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
    list_display = ['name', 'category', 'price', 'stock_quantity', 'image', 'available', 'created_at']
    list_filter = ['available', 'created_at', 'category']
    list_editable = ['price', 'stock_quantity', 'image', 'available']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']
    
    fieldsets = (
        (None, {'fields': ('name', 'slug', 'category', 'description')}),
        ('Pricing & Stock', {'fields': ('price', 'stock', 'available')}),
    )

# --- 3. Order Item Inline for Order Admin ---
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    readonly_fields = ['price', 'quantity', 'get_cost']
    extra = 0
    
    def get_cost(self, obj):
        return obj.get_cost()
    get_cost.short_description = 'Item Cost'

# --- 4. Order Admin (Tracking Payments) ---
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'full_name', 'email', 'paid', 'paystack_ref', 'created_at']
    list_filter = ['paid', 'created_at']
    search_fields = ['id', 'user__username', 'paystack_ref']
    inlines = [OrderItemInline]
    readonly_fields = ['user', 'paystack_ref', 'get_total_cost']
    
    def get_total_cost(self, obj):
        return obj.get_total_cost()
    get_total_cost.short_description = 'Total Order Cost'