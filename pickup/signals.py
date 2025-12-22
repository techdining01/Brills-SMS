from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PickupVerificationLog
from .utils import send_sms  

@receiver(post_save, sender=PickupVerificationLog)
def notify_parent(sender, instance, created, **kwargs):
    if created and instance.status == "SUCCESS":
        parent = instance.pickup.parent
        message = (
            f"Pickup verified for your child(ren). "
            f"Bearer: {instance.pickup.bearer_name}, "
            f"Reference: {instance.pickup.reference}"
        )
        send_sms(parent.phone_number, message)
