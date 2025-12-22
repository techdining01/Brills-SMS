import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
import requests
from django.conf import settings

def generate_pickup_qr(pickup):
    qr = qrcode.make(f"PICKUP:{pickup.reference}")
    buffer = BytesIO()
    qr.save(buffer, format="PNG")

    filename = f"pickup_{pickup.reference}.png"
    pickup.qrcode_image.save(
        filename,
        ContentFile(buffer.getvalue()),
        save=False
    )


def send_sms(phone_number, message):
    url = "https://termii.com/api/sms/send"
    data = {
        "to": phone_number,
        "from": settings.TERMII_SENDER_ID,
        "sms": message,
        "type": "plain",
        "api_key": settings.TERMII_API_KEY
    }
    response = requests.post(url, json=data)
    return response.json()
