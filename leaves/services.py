from .models import LeaveRequest
from datetime import date



ANNUAL_LEAVE_DAYS = 20


def has_overlapping_leave(payee, start_date, end_date):
    return LeaveRequest.objects.filter(
        payee=payee,
        status__in=["pending", "approved"],
        start_date__lte=end_date,
        end_date__gte=start_date,
    ).exists()



def calculate_leave_balance(payee, year=None):
    if not year:
        year = date.today().year

    approved = LeaveRequest.objects.filter(
        payee=payee,
        status="approved",
        start_date__year=year
    )

    used_days = sum(l.days for l in approved)
    return max(ANNUAL_LEAVE_DAYS - used_days, 0)
