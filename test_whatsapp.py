#!/usr/bin/env python3
"""Direct WhatsApp test - no Streamlit"""

from sms_email import send_whatsapp_payment_receipt
from datetime import datetime

# Test WhatsApp receipt directly
success, message = send_whatsapp_payment_receipt(
    "7702031818", "Test Student", 1000, "CMA00001", 
    "1 Month - 8", datetime.now().strftime('%Y-%m-%d'), "Next Due: 01-10-2024"
)

print(f"WhatsApp Success: {success}")
print(f"WhatsApp Message: {message}")