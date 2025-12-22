from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Order, PaymentTransaction, Product, BrillsPayLog, Transaction
from exams.models import ExamAccess
from django.db.models import Sum
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model


User = get_user_model()

def is_admin(user):
    return user.is_authenticated and user.role == "ADMIN"



@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    total_sales = Transaction.objects.filter(
        status="SUCCESS"
    ).aggregate(total=Sum("amount"))["total"] or 0

    total_orders = Order.objects.count()
    total_transactions = Transaction.objects.count()
    total_products = Product.objects.count()

    recent_orders = Order.objects.select_related(
        "user", "ward"
    ).order_by("-created_at")[:5]

    low_stock = Product.objects.filter(stock_quantity__lte=5)

    monthly = (
        Transaction.objects.filter(status="SUCCESS")
        .extra(select={"month": "strftime('%%Y-%%m', created_at)"})
        .values("month")
        .annotate(total=Sum("amount"))
    )

    class_based = (
        Order.objects.values("ward__student_class__name")
        .annotate(total=Sum("total_amount"))
    )



    return render(
        request,
        "brillspay/admin/dashboard.html",
        {
            "total_sales": total_sales,
            "total_orders": total_orders,
            "total_transactions": total_transactions,
            "total_products": total_products,
            "recent_orders": recent_orders,
            "low_stock": low_stock,
            "monthly": monthly,
            "class_based": class_based
        }
    )




@staff_member_required
def admin_add_product(request):
    if request.method == "POST":
        Product.objects.create(
            name=request.POST["name"],
            category_id=request.POST["category"],
            price=request.POST["price"],
            stock_quantity=request.POST["stock"]
        )
        messages.success(request, "Product added")
        return redirect("brillspay:admin_product_list")

    return render(request, "brillspay/admin/products/add.html")


@staff_member_required
def admin_edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        product.name = request.POST["name"]
        product.price = request.POST["price"]
        product.stock_quantity = request.POST["stock"]
        product.save()
        messages.success(request, "Product updated")
        return redirect("brillspay:admin_product_list")

    return render(request, "brillspay/admin/products/edit.html", {
        "product": product
    })


@staff_member_required
def admin_delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    messages.success(request, "Product deleted")
    return redirect("brillspay:admin_product_list")



@staff_member_required
def admin_add_stock(request, pk):
    product = get_object_or_404(Product, pk=pk)
    qty = int(request.POST.get("quantity", 0))
    product.stock_quantity += qty
    product.save()
    return redirect("brillspay:admin_product_list")


@staff_member_required
def admin_remove_stock(request, pk):
    product = get_object_or_404(Product, pk=pk)
    qty = int(request.POST.get("quantity", 0))
    product.stock_quantity = max(0, product.stock_quantity - qty)
    product.save()
    return redirect("brillspay:admin_product_list")


@staff_member_required
def admin_order_list(request):
    orders = Order.objects.select_related("buyer", "ward")
    return render(request, "brillspay/admin/orders/list.html", {
        "orders": orders
    })


@staff_member_required
def admin_order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, "brillspay/admin/orders/detail.html", {
        "order": order
    })


@staff_member_required
def admin_payment_list(request):
    payments = PaymentTransaction.objects.all()
    return render(request, "brillspay/admin/payments/list.html", {
        "payments": payments
    })


@staff_member_required
def admin_transaction_logs(request):
    logs = BrillsPayLog.objects.select_related("user", "order")
    return render(request, "brillspay/admin/logs/list.html", {
        "logs": logs
    })


@login_required
@user_passes_test(is_admin)
def admin_access_list(request):
    accesses = ExamAccess.objects.select_related(
        "student", "exam"
    ).order_by("-granted_at")

    return render(
        request,
        "brillspay/admin/access_list.html",
        {"accesses": accesses}
    )


@login_required
@user_passes_test(is_admin)
def admin_payment_detail(request, tx_id):
    tx = get_object_or_404(
        PaymentTransaction.objects.select_related(
            "order", "user"
        ).prefetch_related(
            "order__items__product"
        ),
        id=tx_id
    )

    return render(
        request,
        "brillspay/admin/payment_detail.html",
        {"tx": tx}
    )



@login_required
@user_passes_test(is_admin)
def admin_revoke_access(request, access_id):
    access = get_object_or_404(ExamAccess, id=access_id)

    access.delete()

    messages.success(
        request,
        f"Access revoked for {access.student.get_full_name()}"
    )

    return redirect("brillspay:admin_access_list")



@staff_member_required
def admin_grant_access(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # Example: Exam unlock
    ExamAccess.objects.get_or_create(
        student=order.ward,
        exam=order.exam,
        defaults={"granted_by": request.user}
    )

    order.status = "FULFILLED"
    order.save()

    BrillsPayLog.objects.create(
        user=request.user,
        order=order,
        action="ADMIN_OVERRIDE",
        message="Access granted manually"
    )

    messages.success(request, "Access granted")
    return redirect("brillspay:admin_order_detail", pk=order.id)



@staff_member_required
def admin_analytics_dashboard(request):
    qs = PaymentTransaction.objects.filter(
        paystack_status="SUCCESS"
    ).values("created_at__date").annotate(
        total=Sum("amount")
    )

    labels = [str(x["created_at__date"]) for x in qs]
    data = [x["total"] for x in qs]

    return render(request, "brillspay/admin/analytics.html", {
        "labels": labels,
        "data": data
    })

