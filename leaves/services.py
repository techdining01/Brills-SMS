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



def calculate_leave_balance(payee, leave_type=None, year=None):
    if not year:
        year = date.today().year

    qs = LeaveRequest.objects.filter(
        payee=payee,
        status="approved",
        start_date__year=year
    )
    
    if leave_type:
        qs = qs.filter(leave_type=leave_type)
        total_allowed = leave_type.annual_days
    else:
        total_allowed = ANNUAL_LEAVE_DAYS

    used_days = sum(l.duration() for l in qs)
    
    return {
        "total": total_allowed,
        "used": used_days,
        "remaining": max(total_allowed - used_days, 0)
    }
