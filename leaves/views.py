from django.shortcuts import render, get_object_or_404
from django.http.response import JsonResponse
from .forms import LeaveRequestForm
from .models import LeaveRequest
from payroll.models import AuditLog, StaffProfile
from django.contrib.auth.decorators import login_required





@login_required
def staff_apply_leave(request):
    staff = request.user.staffprofile

    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.staff = staff
            leave.save()

            AuditLog.objects.create(
                user=request.user,
                action="LEAVE_APPLIED",
                description=f"{leave.leave_type} {leave.start_date} → {leave.end_date}"
            )

            return JsonResponse({"ok": True})

        return JsonResponse({"ok": False, "errors": form.errors})

    return render(request, "leaves/staff/leave_apply.html", {
        "form": LeaveRequestForm(),
        "leaves": LeaveRequest.objects.filter(staff=staff).order_by("-applied_at")
    })


@login_required
def staff_leave_history(request):
    staff = get_object_or_404(StaffProfile, id=request.user.id)
    leaves = LeaveRequest.objects.filter(staff=staff).order_by("-applied_at")
    return render(request, "leaves/staff/ajax_leave_history.html", {"leaves": leaves})

