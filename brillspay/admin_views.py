from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Order


@staff_member_required
def admin_orders(request):
    orders = Order.objects.select_related("buyer", "ward").order_by("-created_at")
    return render(request, "brillspay/admin/orders.html", {"orders": orders})


@staff_member_required
def admin_order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)

    if request.method == "POST" and "override" in request.POST:
        order.status = "OVERRIDDEN"
        order.save()

    return render(request, "brillspay/admin/order_detail.html", {"order": order})


# admin_views.py

from exams.models import ExamAccess
from django.contrib import messages


@staff_member_required
def admin_order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)

    if request.method == "POST" and "override_exam" in request.POST:
        ExamAccess.objects.get_or_create(
            student=order.ward,
            exam=order.exam,
            defaults={"granted_by": request.user}
        )

        order.status = "OVERRIDDEN"
        order.save()

        messages.success(request, "Exam access granted manually")

    return render(request, "brillspay/admin/order_detail.html", {
        "order": order
    })
