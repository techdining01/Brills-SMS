
from payroll.models import Payee, StaffProfile

def register_user_to_payroll(*, user, payee_type, created_by):
    payee = Payee.objects.create(
        user=user,
        payee_type=payee_type,
        full_name=user.get_full_name(),
        reference_code=f"PAYEE-{user.id}"
    )

    StaffProfile.objects.create(
        payee=payee,
        date_of_employment=user.date_joined,
        is_confirmed=True,
    )

    return payee
