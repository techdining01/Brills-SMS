import uuid
from datetime import datetime, timedelta
from io import BytesIO
from django.utils import timezone
import qrcode
from PIL import Image

from django.db import models
from django.db.models import Q
from django.core.files import File
from django.contrib.auth import get_user_model
from .utils import generate_qrcode

# Get our custom User model
User = get_user_model()

class PickupCode(models.Model):
    # The unique, human-readable code
    code = models.UUIDField(
        default=uuid.uuid4, 
        unique=True, 
        editable=False, 
        verbose_name="Verification Code"
    )
    # The parent who generated the code
    parent = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        limit_choices_to=Q(role ='PARENT'),
        related_name='pickup_requests'
    )
    # The child being picked up
    student = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        limit_choices_to=Q(role ='STUDENT'),
        related_name='pickup_authorizations'
    )
    
    # Time-sensitive fields (11-hour logic)
    generated_at = models.DateTimeField(auto_now_add=True)
    # Set the expiry to 11 hours after creation
    expires_at = models.DateTimeField(editable=False) 
    
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        limit_choices_to=Q(role__in = ['ADMIN', 'STAFF']),
        related_name='verifications'
    )
    
    # Store the generated QR code image
    qr_code = models.ImageField(upload_to='pickup_qrcodes', blank=True, null=True)

    def save(self, *args, **kwargs):
        # 1. Set the expiration time if this is a new record
        if not self.pk:
            self.expires_at = datetime.now() + timedelta(hours=11)
        
        # 2. Generate the QR code if it doesn't exist
        if not self.qr_code:
            self.generate_qr_code()
            
        super().save(*args, **kwargs)

    def generate_qr_code(self):
        """Generates the QR code and saves it to the ImageField."""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        # The data encoded in the QR code will be the UUID
        qr.add_data(str(self.code)) 
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save the image to an in-memory buffer
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        
        # Create a Django File object from the buffer and save it to the field
        filename = f'pickup_code_{self.code}.png'
        self.qr_code.save(filename, File(buffer), save=False)

    def is_expired(self):
        return self.expires_at < timezone.now()

    def is_valid(self):
        """Check if the code is not verified AND not expired."""
        return not self.is_verified and not self.is_expired()

    def __str__(self):
        return f"Code for {self.student.username} (Parent: {self.parent.username})"

