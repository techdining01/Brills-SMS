from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Order, Transaction, Product, BrillsPayLog, PaymentTransaction
from exams.models import ExamAccess
from django.db.models import Sum
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.db.models.functions import TruncMonth
from django.utils.timezone import now
from .forms import ProductForm
from django.utils import timezone
from datetime import timedelta
from django.http import HttpResponse
import csv

User = get_user_model()

def is_admin(user):
    return user.is_authenticated and user.role == "ADMIN"



@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):

    # ✅ correct status value
    total_sales = Transaction.objects.filter(
        status="success", verified=True
    ).aggregate(total=Sum("amount"))["total"] or 0

    total_orders = Order.objects.count()
    total_transactions = Transaction.objects.count()
    total_products = Product.objects.count()

    recent_orders = Order.objects.select_related(
        "buyer", "ward"
    ).order_by("-created_at")[:5]

    # ===== Monthly Revenue =====
    monthly_qs = (
        Transaction.objects
        .filter(status="success", verified=True)
        .annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(total=Sum("amount"))
        .order_by("month")
    )

    monthly_labels = [
        m["month"].strftime("%b %Y") for m in monthly_qs
    ]
    monthly_data = [
        float(m["total"]) for m in monthly_qs
    ]

    # ===== Class-based Revenue =====
    class_qs = (
        Order.objects
        .filter(status="PAID")
        .values("ward__student_class__name")
        .annotate(total=Sum("total_amount"))
    )

    class_labels = [
        c["ward__student_class__name"] or "Unknown"
        for c in class_qs
    ]
    class_data = [
        float(c["total"]) for c in class_qs
    ]

    return render(
        request,
        "brillspay/admin/dashboard.html",
        {
            "total_sales": total_sales,
            "total_orders": total_orders,
            "total_transactions": total_transactions,
            "total_products": total_products,
            "recent_orders": recent_orders,

            # charts
            "monthly_labels": monthly_labels,
            "monthly_data": monthly_data,
            "class_labels": class_labels,
            "class_data": class_data,
        }
    )



@staff_member_required
def admin_add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("brillspay:admin_product_list")
    else:
        form = ProductForm()

    return render(request,
        "brillspay/admin/products/add.html", {"form": form}
    )


@staff_member_required
def admin_product_list(request):
    products = (
        Product.objects
        .select_related("category")
        .order_by("-created_at")
    )

    return render(
        request,
        "brillspay/admin/products/product_list.html",
        {
            "products": products
        }
    )


@staff_member_required
def admin_product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect("brillspay:admin_product_list")
    else:
        form = ProductForm(instance=product)

    return render(
        request,
        "brillspay/admin/products/product_edit.html",
        {
            "form": form,
            "product": product
        }
    )



@staff_member_required
def admin_product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        product.delete()
        messages.success(request, f'{product.name} deleted successfully')
        return redirect("brillspay:admin_product_list")

    return render(
        request,
        "brillspay/admin/products/product_confirm_delete.html",
        {
            "product": product
        }
    )



# @staff_member_required
# def admin_edit_product(request, pk):
#     product = get_object_or_404(Product, pk=pk)

#     if request.method == "POST":
#         product.name = request.POST["name"]
#         product.price = request.POST["price"]
#         product.stock_quantity = request.POST["stock"]
#         product.save()
#         messages.success(request, "Product updated")
#         return redirect("brillspay:admin_product_list")

#     return render(request, "brillspay/admin/products/edit.html", {
#         "product": product
#     })


# @staff_member_required
# def admin_delete_product(request, pk):
#     product = get_object_or_404(Product, pk=pk)
#     product.delete()
#     messages.success(request, "Product deleted")
#     return redirect("brillspay:admin_product_list")



# @staff_member_required
# def admin_add_stock(request, pk):
#     product = get_object_or_404(Product, pk=pk)
#     qty = int(request.POST.get("quantity", 0))
#     product.stock_quantity += qty
#     product.save()
#     return redirect("brillspay:admin_product_list")


# @staff_member_required
# def admin_remove_stock(request, pk):
#     product = get_object_or_404(Product, pk=pk)
#     qty = int(request.POST.get("quantity", 0))
#     product.stock_quantity = max(0, product.stock_quantity - qty)
#     product.save()
#     return redirect("brillspay:admin_product_list")


@staff_member_required
def admin_order_list(request):
    orders = Order.objects.select_related("buyer", "ward").order_by('-created_at')
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
    payments = Transaction.objects.all().order_by('-created_at')
    return render(request, "brillspay/admin/payments/list.html", {
        "payments": payments
    })


@staff_member_required
def admin_transaction_logs(request):
    logs = BrillsPayLog.objects.select_related("user", "order").order_by('-created_at')
    return render(request, "brillspay/admin/logs/list.html", {
        "logs": logs
    })


@login_required
@user_passes_test(is_admin)
def admin_access_list(request):
    accesses = ExamAccess.objects.select_related(
        "student", "exam"
    ).order_by("-granted_by")

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
    range_days = int(request.GET.get("range", 7))
    start_date = timezone.now().date() - timedelta(days=range_days)

    qs = (
        Transaction.objects
        .filter(
            status="success",
            verified=True,
            created_at__date__gte=start_date
        )
        .values("created_at__date")
        .annotate(total=Sum("amount"))
        .order_by("created_at__date")
    )

    labels = [str(x["created_at__date"]) for x in qs]
    data = [float(x["total"]) for x in qs]

    total_revenue = sum(data)

    return render(request, "brillspay/admin/analytics.html", {
        "labels": labels,
        "data": data,
        "total_revenue": total_revenue,
        "range_days": range_days,
    })


@staff_member_required
def export_revenue_csv(request):
    qs = (
        Transaction.objects
        .filter(status="success", verified=True)
        .values("created_at__date")
        .annotate(total=Sum("amount"))
        .order_by("created_at__date")
    )

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="revenue_report.csv"'

    writer = csv.writer(response)
    writer.writerow(["Date", "Revenue (₦)"])

    for row in qs:
        writer.writerow([row["created_at__date"], row["total"]])

    return response

