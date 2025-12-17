@login_required
def teacher_analytics(request):
    exams = Exam.objects.filter(created_by=request.user)

    data = []
    for exam in exams:
        attempts = ExamAttempt.objects.filter(exam=exam)
        pending = StudentAnswer.objects.filter(
            question__exam=exam,
            question__type="subjective",
            subjectivemark__isnull=True
        ).count()

        data.append({
            "exam": exam,
            "attempts": attempts.count(),
            "pending": pending
        })

    return render(request, "exams/teacher/analytics.html", {"data": data})
