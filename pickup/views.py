from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import PickupAuthorization, PickupStudent, PickupVerificationLog
from .utils import generate_pickup_qr
import uuid
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.models import User


def is_parent(user):
    return user.is_authenticated and user.role == "PARENT"

def is_admin_or_staff(user):
    return user.is_authenticated and user.role in ["ADMIN", "STAFF"]



import logging
logger = logging.getLogger("system")


@login_required
@user_passes_test(is_parent)
def parent_dashboard(request):
    pickups = PickupAuthorization.objects.filter(parent=request.user).order_by("-created_at")

    return render(request, "pickups/parent/dashboard.html", {
        "pickups": pickups
    })



@login_required
def create_pickup(request):
    if request.user.role != "PARENT":
        return redirect("pickups:qr_scan")

    if request.method == "POST":
        bearer_name = request.POST["bearer_name"]
        relationship = request.POST["relationship"]
        student_ids = request.POST.getlist("students")

        pickup = PickupAuthorization.objects.create(
            parent=request.user,
            bearer_name=bearer_name,
            relationship=relationship,
            expires_at=timezone.now() + timedelta(hours=11),
        )

        for sid in student_ids:
            PickupStudent.objects.create(
                pickup=pickup, student_id=sid
            )

        generate_pickup_qr(pickup)
        pickup.save()

        return redirect("pickups:pickup_detail", pickup.id)

    students = request.user.children.all()

    return render(request, "pickups/parent/create.html", {
        "students": students
    })


# @login_required
# @user_passes_test(is_parent)
# def generate_pickup_code(request):
#     if request.method == "POST":
#         student_ids = request.POST.getlist("students")
#         bearer_name = request.POST.get("bearer_name")
#         relationship = request.POST.get("relationship")

#         expires_at = timezone.now() + timedelta(hours=11)

#         pickup = PickupAuthorization.objects.create(
#             parent=request.user,
#             bearer_name=bearer_name,
#             relationship=relationship,
#             expires_at=expires_at
#         )

#         PickupAuthorization.students.set(student_ids)
#         pickup.generate_qr()   # method on model
#         pickup.save()

#         messages.success(request, "Pickup code generated successfully")
#         return redirect("pickups:parent_dashboard")

#     students = User.objects.filter(
#         parents=request.user,
#         role="STUDENT"
#     )

#     return render(request, "pickups/parent/generate.html", {
#         "students": students
#     })

@login_required
def verify_pickup(request, reference):
    pickup = get_object_or_404(PickupAuthorization, reference=reference)
    if pickup.is_expired() or pickup.is_used:
        return render(request, "pickups/admin/error.html", {"msg": "Expired or already used"})
    if request.method == "POST":
        pickup.is_used = True
        pickup.save()
        PickupVerificationLog.objects.create(
            pickup=pickup,
            verified_by=request.user,
            status="SUCCESS"
        )
        return redirect("pickups:admin_pickup_logs")
    return render(request, "pickups/admin/verify.html", {"pickup": pickup})


@login_required
def pickup_history(request):
    pickups = request.user.PickupAuthorization.order_by('-created_at')
    return render(request, "pickups/parent/history.html", {"pickups": pickups})



@login_required
def verify_pickup_detail(request, code):
    try:
        pickup = PickupAuthorization.objects.select_related("parent").get(
            reference=code
        )
    except PickupAuthorization.DoesNotExist:
        PickupVerificationLog.objects.create(
            pickup=None,
            verified_by=request.user,
            status="INVALID"
        )
        return render(request, "pickups/admin/error.html")

    if pickup.is_used:
        status = "USED"
    elif pickup.is_expired():
        status = "EXPIRED"
    else:
        status = "SUCCESS"
        pickup.is_used = True
        pickup.save()

    PickupVerificationLog.objects.create(
        pickup=pickup,
        verified_by=request.user,
        status=status
    )

    if status != "SUCCESS":
        return render(
            request,
            "pickups/admin/error.html",
            {"pickup": pickup, "status": status}
        )

    return render(
        request,
        "pickups/admin/verify_detail.html",
        {"pickup": pickup}
    )


@login_required
def admin_pickup_logs(request):
    logs = PickupVerificationLog.objects.select_related(
        "pickup", "verified_by"
    ).order_by("-verified_at")
    return render(request, "pickups/admin/logs.html", {"logs": logs})


@login_required
@user_passes_test(is_admin_or_staff)
def qr_scan_page(request):
    return render(request, "pickups/admin/scan.html")



@login_required
def qr_lookup_api(request):
    ref = request.GET.get("ref")

    if not ref:
        return JsonResponse({"error": "No reference"}, status=400)

    try:
        pickup = PickupAuthorization.objects.get(reference=ref)
    except PickupAuthorization.DoesNotExist:
        return JsonResponse({"status": "INVALID"})

    if pickup.is_used:
        return JsonResponse({"status": "USED"})

    if pickup.is_expired():
        return JsonResponse({"status": "EXPIRED"})

    return JsonResponse({
        "status": "VALID",
        "bearer": pickup.bearer_name,
        "relationship": pickup.relationship,
        "students": [
            {
                "name": s.student.get_full_name(),
                "class": getattr(s.student.student_class, "name", ""),
            }
            for s in pickup.students.select_related("student")
        ]
    })

@login_required
@user_passes_test(is_admin_or_staff)
@require_POST
def force_expire_pickup(request):
    code = request.POST.get("code")

    pickup = get_object_or_404(PickupAuthorization, code=code)
    pickup.expires_at = timezone.now()
    pickup.save()

    messages.success(request, "Pickup expired successfully")
    return redirect("pickups:verify_pickup")
