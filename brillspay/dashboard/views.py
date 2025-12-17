@staff_member_required
def admin_analytics(request):
    revenue = (
        Order.objects
        .filter(status="PAID")
        .extra({"day": "date(created_at)"})
        .values("day")
        .annotate(total=Sum("total_amount"))
        .order_by("day")
    )

    exams = Exam.objects.count()
    attempts = ExamAttempt.objects.count()

    return render(request, "dashboard/admin/analytics.html", {
        "revenue": list(revenue),
        "exam_count": exams,
        "attempt_count": attempts
    })
