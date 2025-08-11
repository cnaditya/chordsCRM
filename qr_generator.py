import qrcode
import os
from PIL import Image

def generate_qr_code(student_id):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(student_id)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Create QR codes directory if it doesn't exist
    os.makedirs("qr_codes", exist_ok=True)
    
    filename = f"qr_codes/{student_id}.png"
    img.save(filename)
    return filename