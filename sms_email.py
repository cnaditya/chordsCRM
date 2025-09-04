import requests
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

FAST2SMS_API_KEY = "uC9zfouowPaNrHpOtk5hnVSYiSE9oiihlA7Lld1tBKd49RuUdQusN45x0oPX"

def send_whatsapp(template, mobile, variables_list):
    """Clean WhatsApp function following exact Fast2SMS format"""
    url = "https://www.fast2sms.com/dev/whatsapp"
    
    template_map = {
        "fee_reminder": "5170",
        "payment_receipt": "5171"
    }

    message_id = template_map.get(template)
    if not message_id:
        return False, f"Unknown template: {template}"

    # Clean mobile number
    mobile = str(mobile).replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if len(mobile) == 10:
        mobile = "91" + mobile

    variables_values = "|".join(variables_list)
    params = {
        "authorization": FAST2SMS_API_KEY,
        "message_id": message_id,
        "numbers": mobile,
        "variables_values": variables_values
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"DEBUG: Status={response.status_code}, Response={response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("return") is True:
                return True, f"WhatsApp {template} sent successfully"
            else:
                return False, f"API error: {result}"
        else:
            return False, f"HTTP {response.status_code}: {response.text}"
    except Exception as e:
        return False, f"Network error: {str(e)}"

def send_whatsapp_reminder(mobile, student_name, plan, expiry_date, include_qr=False):
    """Send fee reminder using template 5170"""
    
    # Format date to dd-mm-yyyy
    if " 00:00:00" in str(expiry_date):
        expiry_date = str(expiry_date).replace(" 00:00:00", "")
    
    try:
        date_obj = datetime.strptime(str(expiry_date), '%Y-%m-%d')
        expiry_date_formatted = date_obj.strftime('%d-%m-%Y')
    except:
        expiry_date_formatted = str(expiry_date)
    
    # Template 5170: student_name|plan|expiry_date
    variables_list = [student_name, plan, expiry_date_formatted]
    
    return send_whatsapp("fee_reminder", mobile, variables_list)

def send_whatsapp_payment_receipt(mobile, student_name, amount, receipt_no, plan, payment_date, next_due_info):
    """Send payment receipt using template 5171"""
    
    print(f"RECEIPT FUNCTION CALLED: {student_name}, {mobile}, {amount}")
    
    # Format payment date
    try:
        date_obj = datetime.strptime(str(payment_date), '%Y-%m-%d')
        payment_date_formatted = date_obj.strftime('%d-%m-%Y')
    except:
        payment_date_formatted = str(payment_date)
    
    # Template 5171: student_name|amount|receipt_no|plan|payment_date|next_due_info
    variables_list = [student_name, str(amount), receipt_no, plan, payment_date_formatted, next_due_info]
    
    print(f"RECEIPT VARIABLES: {variables_list}")
    
    return send_whatsapp("payment_receipt", mobile, variables_list)

def test_fast2sms():
    """Test Fast2SMS API"""
    print("TESTING Fast2SMS API...")
    
    # Test fee reminder
    success, message = send_whatsapp(
        template="fee_reminder",
        mobile="7702031818",
        variables_list=["Test", "Package", "01-09-2025"]
    )
    
    print(f"Test Result: {success}")
    print(f"Message: {message}")
    return 200 if success else 400, message

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