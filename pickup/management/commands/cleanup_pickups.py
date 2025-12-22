from django.core.management.base import BaseCommand
from django.utils import timezone
from pickup.models import PickupAuthorization


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        expired = PickupAuthorization.objects.filter(
            expires_at__lt=timezone.now(),
            is_used=False
        )
        count = expired.count()
        expired.update(is_used=True)
        self.stdout.write(f"{count} pickups auto-expired")
