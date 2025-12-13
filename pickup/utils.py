import qrcode
import base64
from io import BytesIO

def generate_qrcode(data):
    """Generates a QR code for the given data and returns it as a base64 string."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save image to an in-memory buffer
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    
    # Encode the image data to base64
    return base64.b64encode(buffer.getvalue()).decode()