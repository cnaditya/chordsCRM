import requests
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Use environment variable for API key (fallback to hardcoded for now)
FAST2SMS_API_KEY = os.getenv("FAST2SMS_API_KEY", "6TDScuetHNniG5F92kswhvrLJx4IAVRjpoZUb1Y83CzBl0WEd7RLDaifTQwBqekSC2vnMz583p4lKsdX")

def send_whatsapp_reminder(mobile, student_name, plan, expiry_date, include_qr=False):
    """Send WhatsApp reminder using Fast2SMS template - FINAL CLEAN VERSION"""
    
    print(f"FUNCTION CALLED: send_whatsapp_reminder for {student_name} at {mobile}")
    
    # Clean and normalize mobile number
    mobile = str(mobile).replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if len(mobile) == 10 and mobile.isdigit():
        mobile = "91" + mobile
    elif mobile.startswith("+"):
        mobile = mobile[1:]
    
    if not mobile.isdigit() or len(mobile) < 10:
        return False, f"Invalid mobile number format: {mobile}"
    
    # Format date YYYY-MM-DD → DD-MM-YYYY
    if " 00:00:00" in str(expiry_date):
        expiry_date = str(expiry_date).replace(" 00:00:00", "")
    
    try:
        date_obj = datetime.strptime(str(expiry_date), '%Y-%m-%d')
        expiry_date_formatted = date_obj.strftime('%d-%m-%Y')
    except:
        expiry_date_formatted = str(expiry_date)
    
    # Choose template dynamically
    message_id = "4899" if include_qr else "3004"  # Use 3004 as primary
    
    # Build variables string - no empty values
    variables = f"{student_name}|{plan}|{expiry_date_formatted}"
    
    url = "https://www.fast2sms.com/dev/whatsapp"
    
    # API key in headers (NOT query params)
    headers = {
        "authorization": FAST2SMS_API_KEY
    }
    
    # Clean parameters - NO sender_id
    params = {
        "message_id": message_id,
        "numbers": mobile,
        "variables_values": variables
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        # Debug logging
        print(f"DEBUG {message_id}: URL={url}")
        print(f"DEBUG {message_id}: Headers={headers}")
        print(f"DEBUG {message_id}: Params={params}")
        print(f"DEBUG {message_id}: Status={response.status_code}")
        print(f"DEBUG {message_id}: Response={response.text}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                if result.get('return') == True:
                    return True, f"WhatsApp reminder sent successfully (Template {message_id})"
                else:
                    error_msg = result.get('message', result.get('error', f'API Error: {result}'))
                    return False, f"Template {message_id} Error: {error_msg}"
            except:
                return False, f"Invalid JSON response: {response.text}"
        else:
            return False, f"HTTP {response.status_code}: {response.text}"
    
    except Exception as e:
        print(f"DEBUG {message_id}: Exception: {str(e)}")
        return False, f"Network Error: {str(e)}"

def send_whatsapp_payment_receipt(mobile, student_name, amount, receipt_no, plan, payment_date, next_due_info):
    """Send WhatsApp payment receipt using template 4587"""
    
    # Clean mobile number
    mobile = str(mobile).replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if len(mobile) == 10 and mobile.isdigit():
        mobile = "91" + mobile
    elif mobile.startswith("+"):
        mobile = mobile[1:]
    
    if not mobile.isdigit() or len(mobile) < 10:
        return False, f"Invalid mobile number format: {mobile}"
    
    # Format payment date
    try:
        date_obj = datetime.strptime(str(payment_date), '%Y-%m-%d')
        payment_date_formatted = date_obj.strftime('%d-%m-%Y')
    except:
        payment_date_formatted = str(payment_date)
    
    # Template 4587 variables (6 variables)
    variables = f"{student_name}|{amount}|{receipt_no}|{plan}|{payment_date_formatted}|{next_due_info}"
    
    url = "https://www.fast2sms.com/dev/whatsapp"
    
    headers = {
        "authorization": FAST2SMS_API_KEY
    }
    
    params = {
        "message_id": "4587",
        "numbers": mobile,
        "variables_values": variables
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('return') == True:
                return True, "WhatsApp receipt sent successfully"
            else:
                return False, f"API Error: {result.get('message', 'Unknown error')}"
        else:
            return False, f"HTTP {response.status_code}: {response.text}"
    
    except Exception as e:
        return False, f"Network Error: {str(e)}"

def test_fast2sms():
    """Test Fast2SMS API with clean parameters"""
    print("TESTING Fast2SMS API...")
    
    url = "https://www.fast2sms.com/dev/whatsapp"
    
    headers = {
        "authorization": FAST2SMS_API_KEY
    }
    
    params = {
        "message_id": "3004",
        "numbers": "917702031818",
        "variables_values": "Test|Package|01-01-2025"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        print(f"TEST: Status={response.status_code}")
        print(f"TEST: Response={response.text}")
        print(f"TEST: Headers={headers}")
        print(f"TEST: Params={params}")
        return response.status_code, response.text
    except Exception as e:
        print(f"TEST: Error={e}")
        return None, str(e)

def send_payment_receipt_email(student_email, student_name, amount, receipt_number, plan, student_id=None, instrument=None, start_date=None, expiry_date=None, payment_method="Cash Payment", next_due_date=None):
    """Send payment receipt via Gmail SMTP"""
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