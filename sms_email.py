import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

FAST2SMS_API_KEY = "6TDScuetHNniG5F92kswhvrLJx4IAVRjpoZUb1Y83CzBl0WEd7RLDaifTQwBqekSC2vnMz583p4lKsdX"

def send_whatsapp_reminder(mobile, student_name, plan, expiry_date):
    """Send WhatsApp reminder using Fast2SMS template"""
    
    # Clean and format mobile number for international support
    mobile = str(mobile).replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    
    # Add country code if not present
    if mobile.startswith("+"):
        # Already has country code, remove + for API
        mobile = mobile[1:]
    elif mobile.startswith("91") and len(mobile) == 12:
        # Already has 91 prefix
        pass
    elif len(mobile) == 10 and mobile.isdigit():
        # Indian number without country code, add 91
        mobile = "91" + mobile
    elif not mobile.isdigit():
        return False, f"Invalid mobile number format: {mobile}"
    
    # Validate final format
    if len(mobile) < 10 or len(mobile) > 15 or not mobile.isdigit():
        return False, f"Invalid mobile number: {mobile}. Must be 10-15 digits with country code."
    
    url = "https://www.fast2sms.com/dev/whatsapp"
    
    # Clean and format date to dd-mm-yyyy
    if " 00:00:00" in str(expiry_date):
        expiry_date = str(expiry_date).replace(" 00:00:00", "")
    
    # Convert to dd-mm-yyyy format
    try:
        from datetime import datetime
        date_obj = datetime.strptime(str(expiry_date), '%Y-%m-%d')
        expiry_date_formatted = date_obj.strftime('%d-%m-%Y')
    except:
        expiry_date_formatted = str(expiry_date)
    
    # Using Fast2SMS template 3004 (fees_reminder_new) - MARKETING category
    variables = f"{student_name}|{plan}|{expiry_date_formatted}"
    
    params = {
        "authorization": FAST2SMS_API_KEY,
        "message_id": "3004",
        "numbers": mobile,
        "variables_values": variables,
        "sender_id": "CHORDS"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        # Debug logging
        print(f"DEBUG: URL: {url}")
        print(f"DEBUG: Params: {params}")
        print(f"DEBUG: Status: {response.status_code}")
        print(f"DEBUG: Response: {response.text}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"DEBUG: JSON Result: {result}")
                
                if result.get('return') == True:
                    return True, "WhatsApp reminder sent successfully"
                else:
                    error_msg = result.get('message', result.get('error', 'Unknown API error'))
                    return False, f"API Error: {error_msg}"
            except:
                return False, f"Invalid JSON response: {response.text}"
        else:
            return False, f"HTTP {response.status_code}: {response.text}"
    except Exception as e:
        return False, f"Network Error: {str(e)}"

def send_payment_receipt_email(student_email, student_name, amount, receipt_number, plan, student_id=None, instrument=None, start_date=None, expiry_date=None, payment_method="Cash Payment", next_due_date=None):
    """Send payment receipt via Gmail SMTP using professional template"""
    sender_email = "chords.music.academy@gmail.com"
    sender_password = "xdiu rhua fhpc zwrk"
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = student_email
    msg['Subject'] = "Chords Music Academy - Payment Receipt & Next Due Date"
    
    # Extract class count from plan
    num_classes = plan.split(" - ")[1] if " - " in plan else "N/A"
    
    # Convert dates to dd-mm-yyyy format
    def format_date(date_str):
        try:
            if date_str and date_str != 'N/A':
                date_obj = datetime.strptime(str(date_str).split(' ')[0], '%Y-%m-%d')
                return date_obj.strftime('%d-%m-%Y')
        except:
            pass
        return date_str or 'N/A'
    
    start_date_formatted = format_date(start_date)
    expiry_date_formatted = format_date(expiry_date)
    payment_date_formatted = datetime.now().strftime('%d-%m-%Y')
    
    body = f"""Dear {student_name},

Thank you for your payment to Chords Music Academy. We have successfully received your fee. Please find your receipt details below:

---

🧾 Receipt Details

- Receipt Number: {receipt_number}
- Student Name: {student_name}
- Student ID: {student_id or 'N/A'}
- Course/Instrument: {instrument or 'N/A'}
- No. of Classes: {num_classes}
- Class Type: Offline
- Start Date: {start_date_formatted}
- End Date: {expiry_date_formatted}
- 🗓️ Next Due Date: {format_date(next_due_date) if next_due_date else '🎉 NO DUES - FULLY PAID'}

---

💰 Payment Summary

- Total Fees Paid: ₹{amount}
- Payment Date: {payment_date_formatted}
- Payment Method: {payment_method}

---

If you have any questions or need to reschedule your classes, please feel free to contact us:

📞 Phone: +91-7981585309
🌐 Website: www.chordsmusicacademy.in

Thank you for choosing Chords Music Academy. We're thrilled to be part of your musical journey! 🎶

Warm regards,
Aditya CN
Managing Director
🎹 Chords Music Academy
    """
    
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        return True, "Receipt sent to email"
    except Exception as e:
        return False, f"Email error: {str(e)}"