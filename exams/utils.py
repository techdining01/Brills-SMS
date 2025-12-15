from exams.models import ExamAccessOverride
from brillspay.models import Order

def has_paid_for_exam(user, exam):
    return Order.objects.filter(
        user=user,
        is_paid=True,
        exam=exam
    ).exists()


def can_access_exam(user, exam):
    # Mercy override
    if ExamAccessOverride.objects.filter(
        student=user,
        exam=exam,
        is_active=True
    ).exists():
        return True

    # Normal payment path
    if exam.requires_payment:
        return Order.objects.filter(
            user=user,
            exam=exam,
            is_paid=True
        ).exists()

    return True
