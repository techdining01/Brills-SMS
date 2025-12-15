import uuid
from datetime import datetime, timedelta
from io import BytesIO
from django.utils import timezone
import qrcode
from PIL import Image

from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid

User = settings.AUTH_USER_MODEL


class PickupAuthorization(models.Model):
    parent = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="pickup_authorizations"
    )

    reference = models.CharField(
        max_length=20, unique=True, editable=False
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
        if not self.reference:
            self.reference = uuid.uuid4().hex[:12].upper()
        super().save(*args, **kwargs)

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
        User, on_delete=models.SET_NULL, null=True
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

