import uuid
import qrcode
from datetime import datetime, timedelta
from io import BytesIO
from io import BytesIO
from django.utils import timezone
from PIL import Image
from django.db import models
from django.core.files.base import ContentFile
from django.utils import timezone
from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class PickupAuthorization(models.Model):
    parent = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="pickup_authorizations"
    )

    reference = models.CharField(
        max_length=50, unique=True, editable=False
    )

    bearer_name = models.CharField(max_length=100)
    relationship = models.CharField(max_length=50)

    qrcode_image = models.ImageField(
        upload_to="pickup_qrcodes/",
        blank=True,
        null=True
    )

    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        if not self.reference:
            self.reference = uuid.uuid4()

        super().save(*args, **kwargs)

        # generate QR only once
        if is_new and not self.qrcode_image:
            self.generate_qr()

    def generate_qr(self):
        qr_data = f"PICKUP:{self.reference}"

        qr = qrcode.make(qr_data)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")

        filename = f"{self.reference}.png"
        self.qrcode_image.save(
            filename,
            ContentFile(buffer.getvalue()),
            save=True
        )

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return self.reference

class PickupStudent(models.Model):
    pickup = models.ForeignKey(
        PickupAuthorization,
        on_delete=models.CASCADE,
        related_name="students"
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={"role": "STUDENT"}
    )

    def __str__(self):
        return f"{self.student.get_full_name()} → {self.pickup.reference}"


class PickupVerificationLog(models.Model):
    pickup = models.ForeignKey(
        PickupAuthorization, on_delete=models.CASCADE
    )
    verified_by = models.ForeignKey(
        User, on_delete=models.CASCADE
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ("SUCCESS", "Success"),
            ("EXPIRED", "Expired"),
            ("USED", "Already Used"),
            ("INVALID", "Invalid"),
        ]
    )
    verified_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pickup.reference} - {self.status}"

