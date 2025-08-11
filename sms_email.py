import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

FAST2SMS_API_KEY = "6TDScuetHNniG5F92kswhvrLJx4IAVRjpoZUb1Y83CzBl0WEd7RLDaifTQwBqekSC2vnMz583p4lKsdX"

def send_whatsapp_reminder(mobile, student_name, plan, expiry_date):
    """Send WhatsApp reminder using Fast2SMS template"""
    url = "https://www.fast2sms.com/dev/whatsapp"
    
    # Clean and format date to dd-mm-yyyy
    if " 00:00:00" in str(expiry_date):
        expiry_date = str(expiry_date).replace(" 00:00:00", "")
    
    # Convert to dd-mm-yyyy format
    try:
        from datetime import datetime
        date_obj = datetime.strptime(str(expiry_date), '%Y-%m-%d')
        expiry_date = date_obj.strftime('%d-%m-%Y')
    except:
        pass
    
    # Using fees_reminder_new template (ID: 3004)
    # Variables: Var1=student_name, Var2=plan, Var3=expiry_date
    variables = f"{student_name}|{plan}|{expiry_date}"
    
    params = {
        "authorization": FAST2SMS_API_KEY,
        "message_id": "3004",
        "numbers": mobile,
        "variables_values": variables
    }
    
    try:
        response = requests.get(url, params=params)
        print(f"DEBUG: Sending to {mobile}")
        print(f"DEBUG: {response.status_code} - {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('return') == True:
                return True, "WhatsApp reminder sent successfully"
            else:
                return False, f"API Error: {result.get('message', response.text)}"
        else:
            return False, f"HTTP {response.status_code}: {response.text}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def send_payment_receipt_email(student_email, student_name, amount, receipt_number, plan, student_id=None, instrument=None, start_date=None, expiry_date=None, payment_method="Cash Payment"):
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
- 🗓️ Next Due Date: {expiry_date_formatted}

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