from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.crypto import get_random_string
from accounts.models import User
from payroll.models import Payee, StaffProfile

@receiver(post_save, sender=User)
def auto_register_staff_to_payroll(sender, instance, created, **kwargs):
    if not created:
        return

    if instance.role not in ["ADMIN", "TEACHER", "NON_TEACHER"]:
        return

    payee, _ = Payee.objects.get_or_create(
        user=instance,
        defaults={
            "full_name": instance.get_full_name(),
            "payee_type": instance.role.lower(),
            "reference_code": get_random_string(12).upper(),
        }
    )

    StaffProfile.objects.get_or_create(
        payee=payee,
        defaults={
            "phone_number": instance.phone_number or "",
            "date_of_employment": instance.created_at.date(),
        }
    )
