# from exams.models import ExamAccessOverride
from brillspay.models import Order

def has_paid_for_exam(user, exam):
    return Order.objects.filter(
        user=user,
        is_paid=True,
        exam=exam
    ).exists()


 