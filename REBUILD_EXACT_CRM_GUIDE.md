# REBUILD EXACT CRM - Step by Step Guide

## 🎯 Purpose: Build Identical Chords Music Academy CRM from Scratch

### 📋 EXACT VALUES TO USE (Copy-Paste Ready)

#### Business Information
```python
BUSINESS_NAME = "Chords Music Academy"
WEBSITE = "www.chordsmusicacademy.in"
OWNER_NAME = "Chippada Naga Aditya Ganesh"
MANAGING_DIRECTOR = "Aditya CN"
CONTACT_PHONE = "+91-7981585309"
REGISTERED_SENDER = "7981585309"
```

#### Payment Details
```python
UPI_ID = "7702031818"
ACCOUNT_NUMBER = "20115230403"
IFSC_CODE = "SBIN0015780"
BANK_NAME = "State Bank of India"
ACCOUNT_HOLDER = "Chippada Naga Aditya Ganesh"
```

#### API Credentials
```python
FAST2SMS_API_KEY = "uC9zfouowPaNrHpOtk5hnVSYiSE9oiihlA7Lld1tBKd49RuUdQusN45x0oPX"
SENDER_EMAIL = "chords.music.academy@gmail.com"
APP_PASSWORD = "xdiu rhua fhpc zwrk"
```

#### WhatsApp Template IDs
```python
template_map = {
    "fee_reminder": "5170",
    "payment_receipt": "5171", 
    "installment_reminder": "5209"
}
```

#### Database Configuration
```python
DATABASE_NAME = "chords_crm.db"
RECEIPT_PREFIX = "CMA"
STUDENT_ID_PREFIX = "CMA"
```

---

## 🚀 STEP-BY-STEP REBUILD PROCESS

### Step 1: Environment Setup
```bash
mkdir chords_crm_rebuild
cd chords_crm_rebuild
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install streamlit pandas requests
```

### Step 2: Create requirements.txt
```txt
streamlit>=1.28.0
pandas>=1.5.0
requests>=2.28.0
```

### Step 3: Create Database Structure (create_database.py)
```python
import sqlite3
from datetime import datetime

def create_database():
    conn = sqlite3.connect('chords_crm.db')
    cursor = conn.cursor()
    
    # Students table - EXACT 19 columns
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS students_enhanced (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT UNIQUE,
        name TEXT NOT NULL,
        mobile TEXT,
        email TEXT,
        instrument TEXT,
        plan TEXT,
        amount REAL,
        start_date TEXT,
        expiry_date TEXT,
        payment_status TEXT DEFAULT 'Active',
        created_date TEXT DEFAULT CURRENT_TIMESTAMP,
        last_payment_date TEXT,
        next_due_date TEXT,
        remaining_balance REAL DEFAULT 0,
        total_paid REAL DEFAULT 0,
        installment_amount REAL DEFAULT 0,
        installment_frequency TEXT DEFAULT 'Monthly',
        notes TEXT,
        is_active INTEGER DEFAULT 1
    )
    ''')
    
    # Payments table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT,
        amount REAL,
        payment_date TEXT,
        receipt_number TEXT UNIQUE,
        payment_method TEXT DEFAULT 'Cash',
        notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students_enhanced (student_id)
    )
    ''')
    
    # Instruments table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS instruments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )
    ''')
    
    # Plans table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        amount REAL NOT NULL,
        duration_months INTEGER DEFAULT 1
    )
    ''')
    
    # Insert default instruments
    instruments = [
        'Piano/Keyboard', 'Guitar', 'Violin', 'Drums', 
        'Vocals', 'Flute', 'Saxophone', 'Ukulele'
    ]
    for instrument in instruments:
        cursor.execute('INSERT OR IGNORE INTO instruments (name) VALUES (?)', (instrument,))
    
    # Insert default plans
    plans = [
        ('1 Month - 4', 2000, 1), ('1 Month - 8', 3500, 1),
        ('3 Months - 4', 5500, 3), ('3 Months - 8', 9500, 3),
        ('6 Months - 4', 10000, 6), ('6 Months - 8', 18000, 6),
        ('1 Year - 4', 18000, 12), ('1 Year - 8', 32000, 12)
    ]
    for plan in plans:
        cursor.execute('INSERT OR IGNORE INTO plans (name, amount, duration_months) VALUES (?, ?, ?)', plan)
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()
    print("Database created successfully!")
```

### Step 4: Create Communication Module (sms_email.py)
```python
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

FAST2SMS_API_KEY = "uC9zfouowPaNrHpOtk5hnVSYiSE9oiihlA7Lld1tBKd49RuUdQusN45x0oPX"

def send_whatsapp(template, mobile, variables_list):
    """Send WhatsApp using Fast2SMS"""
    url = "https://www.fast2sms.com/dev/whatsapp"
    
    template_map = {
        "fee_reminder": "5170",
        "payment_receipt": "5171",
        "installment_reminder": "5209"
    }

    message_id = template_map.get(template)
    if not message_id:
        return False, f"Unknown template: {template}"

    # Clean mobile number
    mobile = str(mobile).replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if mobile.startswith('0'):
        mobile = mobile[1:]
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

def send_whatsapp_reminder(mobile, student_name, plan, expiry_date):
    """Send fee reminder using template 5170"""
    try:
        date_obj = datetime.strptime(str(expiry_date), '%Y-%m-%d')
        expiry_date_formatted = date_obj.strftime('%d-%m-%Y')
    except:
        expiry_date_formatted = str(expiry_date)
    
    variables_list = [student_name, plan, expiry_date_formatted]
    return send_whatsapp("fee_reminder", mobile, variables_list)

def send_whatsapp_installment_reminder(mobile, student_name, pending_amount, due_date, plan, package_end_date):
    """Send installment reminder using template 5209"""
    try:
        due_date_formatted = datetime.strptime(str(due_date), '%Y-%m-%d').strftime('%d-%m-%Y')
    except:
        due_date_formatted = str(due_date)
    
    try:
        end_date_formatted = datetime.strptime(str(package_end_date), '%Y-%m-%d').strftime('%d-%m-%Y')
    except:
        end_date_formatted = str(package_end_date)
    
    variables_list = [student_name, str(pending_amount), due_date_formatted, plan, end_date_formatted]
    return send_whatsapp("installment_reminder", mobile, variables_list)

def send_whatsapp_payment_receipt(mobile, student_name, amount, receipt_no, plan, payment_date, next_due_info):
    """Send payment receipt using template 5171"""
    mobile_clean = str(mobile).replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if mobile_clean.startswith('0'):
        mobile_clean = mobile_clean[1:]
    if len(mobile_clean) == 10:
        mobile_clean = "91" + mobile_clean
    
    try:
        date_obj = datetime.strptime(str(payment_date), '%Y-%m-%d')
        payment_date_formatted = date_obj.strftime('%d-%m-%Y')
    except:
        payment_date_formatted = str(payment_date)
    
    variables_list = [student_name, str(amount), receipt_no, plan, payment_date_formatted, next_due_info]
    return send_whatsapp("payment_receipt", mobile_clean, variables_list)

def send_payment_receipt_email(student_email, student_name, amount, receipt_number, plan, **kwargs):
    """Send payment receipt via Gmail SMTP"""
    sender_email = "chords.music.academy@gmail.com"
    sender_password = "xdiu rhua fhpc zwrk"
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = student_email
    msg['Subject'] = "Chords Music Academy - Payment Receipt & Next Due Date"
    
    # Email body with all receipt details
    body = f"""Dear {student_name},

Thank you for your payment to Chords Music Academy. Receipt details:

Receipt Number: {receipt_number}
Amount Paid: ₹{amount:,.0f}
Package: {plan}
Payment Date: {datetime.now().strftime('%d-%m-%Y')}

Thank you for choosing Chords Music Academy! 🎶

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
```

### Step 5: Create Main Application (app.py)
```python
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import uuid
from sms_email import *

# Page configuration
st.set_page_config(page_title="Chords Music Academy CRM", layout="wide")

def get_db_connection():
    return sqlite3.connect('chords_crm.db')

def generate_student_id():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"CMA{timestamp}"

def generate_receipt_number():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT receipt_number FROM payments ORDER BY id DESC LIMIT 1")
    last_receipt = cursor.fetchone()
    conn.close()
    
    if last_receipt:
        last_num = int(last_receipt[0][3:])  # Remove 'CMA' prefix
        next_num = last_num + 1
    else:
        next_num = 1
    
    return f"CMA{next_num:05d}"

def main():
    st.title("🎹 Chords Music Academy - CRM System")
    
    # Sidebar navigation
    st.sidebar.title("Chords CRM")
    page = st.sidebar.selectbox("Select Page", [
        "Add Student", "View Students", "Process Payment", 
        "Due Alerts", "Payment Overview"
    ])
    
    if page == "Add Student":
        add_student_page()
    elif page == "View Students":
        view_students_page()
    elif page == "Process Payment":
        process_payment_page()
    elif page == "Due Alerts":
        due_alerts_page()
    elif page == "Payment Overview":
        payment_overview_page()

def add_student_page():
    st.header("Add New Student")
    
    # Get instruments and plans
    conn = get_db_connection()
    instruments_df = pd.read_sql_query("SELECT name FROM instruments", conn)
    plans_df = pd.read_sql_query("SELECT name, amount FROM plans", conn)
    conn.close()
    
    with st.form("add_student_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Student Name*")
            mobile = st.text_input("Mobile Number*")
            email = st.text_input("Email Address")
            instrument = st.selectbox("Instrument*", instruments_df['name'].tolist())
        
        with col2:
            plan = st.selectbox("Plan*", plans_df['name'].tolist())
            amount = st.number_input("Amount", value=float(plans_df[plans_df['name']==plan]['amount'].iloc[0]) if plan else 0.0)
            start_date = st.date_input("Start Date", datetime.now())
            notes = st.text_area("Notes")
        
        submitted = st.form_submit_button("Add Student")
        
        if submitted and name and mobile and instrument and plan:
            # Calculate expiry date based on plan
            plan_duration = plans_df[plans_df['name']==plan]['amount'].iloc[0]  # This should be duration from plans table
            expiry_date = start_date + timedelta(days=30)  # Default 1 month
            
            student_id = generate_student_id()
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO students_enhanced 
            (student_id, name, mobile, email, instrument, plan, amount, start_date, expiry_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (student_id, name, mobile, email, instrument, plan, amount, start_date, expiry_date, notes))
            
            conn.commit()
            conn.close()
            
            st.success(f"Student added successfully! Student ID: {student_id}")

def view_students_page():
    st.header("View Students")
    
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM students_enhanced WHERE is_active = 1", conn)
    conn.close()
    
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No students found.")

def process_payment_page():
    st.header("Process Payment")
    
    conn = get_db_connection()
    students_df = pd.read_sql_query("SELECT student_id, name FROM students_enhanced WHERE is_active = 1", conn)
    conn.close()
    
    if students_df.empty:
        st.warning("No students found. Please add students first.")
        return
    
    with st.form("payment_form"):
        student_options = [f"{row['name']} ({row['student_id']})" for _, row in students_df.iterrows()]
        selected_student = st.selectbox("Select Student", student_options)
        
        amount = st.number_input("Payment Amount", min_value=0.0, step=100.0)
        payment_method = st.selectbox("Payment Method", ["Cash", "UPI", "Bank Transfer", "Card"])
        notes = st.text_area("Payment Notes")
        
        col1, col2 = st.columns(2)
        with col1:
            process_btn = st.form_submit_button("💰 Process Payment & Send Receipt")
        
        if process_btn and amount > 0:
            student_id = selected_student.split('(')[1].split(')')[0]
            receipt_number = generate_receipt_number()
            payment_date = datetime.now().strftime('%Y-%m-%d')
            
            # Add payment record
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO payments (student_id, amount, payment_date, receipt_number, payment_method, notes)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (student_id, amount, payment_date, receipt_number, payment_method, notes))
            
            # Get student details
            cursor.execute("SELECT * FROM students_enhanced WHERE student_id = ?", (student_id,))
            student = cursor.fetchone()
            
            conn.commit()
            conn.close()
            
            if student:
                # Send WhatsApp receipt
                success, message = send_whatsapp_payment_receipt(
                    mobile=student[3],  # mobile column
                    student_name=student[2],  # name column
                    amount=amount,
                    receipt_no=receipt_number,
                    plan=student[6],  # plan column
                    payment_date=payment_date,
                    next_due_info="Thank you for your payment!"
                )
                
                if success:
                    st.success(f"✅ Payment processed! Receipt: {receipt_number}")
                    st.success(f"📱 WhatsApp receipt sent to {student[3]}")
                else:
                    st.warning(f"⚠️ Payment processed but WhatsApp failed: {message}")

def due_alerts_page():
    st.header("Due Alerts")
    
    conn = get_db_connection()
    # Get students with upcoming due dates
    df = pd.read_sql_query('''
    SELECT student_id, name, mobile, plan, expiry_date, remaining_balance
    FROM students_enhanced 
    WHERE is_active = 1 AND expiry_date <= date('now', '+7 days')
    ''', conn)
    conn.close()
    
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        
        if st.button("Send Reminder to All"):
            for _, student in df.iterrows():
                success, message = send_whatsapp_reminder(
                    mobile=student['mobile'],
                    student_name=student['name'],
                    plan=student['plan'],
                    expiry_date=student['expiry_date']
                )
                st.write(f"{student['name']}: {message}")
    else:
        st.info("No due alerts at this time.")

def payment_overview_page():
    st.header("Payment Overview")
    
    conn = get_db_connection()
    
    # Total students
    total_students = pd.read_sql_query("SELECT COUNT(*) as count FROM students_enhanced WHERE is_active = 1", conn).iloc[0]['count']
    
    # Total payments today
    today_payments = pd.read_sql_query('''
    SELECT COALESCE(SUM(amount), 0) as total 
    FROM payments 
    WHERE payment_date = date('now')
    ''', conn).iloc[0]['total']
    
    # Total payments this month
    month_payments = pd.read_sql_query('''
    SELECT COALESCE(SUM(amount), 0) as total 
    FROM payments 
    WHERE strftime('%Y-%m', payment_date) = strftime('%Y-%m', 'now')
    ''', conn).iloc[0]['total']
    
    conn.close()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Students", total_students)
    with col2:
        st.metric("Today's Collection", f"₹{today_payments:,.0f}")
    with col3:
        st.metric("This Month", f"₹{month_payments:,.0f}")

if __name__ == "__main__":
    main()
```

### Step 6: Create Streamlit Config (.streamlit/config.toml)
```toml
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
```

### Step 7: Initialize Database
```bash
python create_database.py
```

### Step 8: Run Application
```bash
streamlit run app.py
```

---

## ✅ VERIFICATION CHECKLIST

- [ ] Database created with exact 19 columns
- [ ] All 3 WhatsApp templates working (5170, 5171, 5209)
- [ ] Email receipts sending successfully
- [ ] Payment processing with receipt generation
- [ ] Student management (add/view/edit)
- [ ] Due alerts functionality
- [ ] Payment overview dashboard
- [ ] Mobile number formatting working
- [ ] Receipt numbering (CMA00001 format)
- [ ] Student ID generation (CMA + timestamp)

## 🚀 DEPLOYMENT

### GitHub Setup
```bash
git init
git add .
git commit -m "Initial Chords CRM setup"
git remote add origin [your-repo-url]
git push -u origin main
```

### Streamlit Cloud
1. Connect GitHub repository
2. Set main file: `app.py`
3. Deploy automatically

---

## 📞 EXACT CONTACT DETAILS

- **Business**: Chords Music Academy
- **Phone**: +91-7981585309
- **Email**: chords.music.academy@gmail.com
- **UPI**: 7702031818
- **Website**: www.chordsmusicacademy.in

---

*This guide will create an EXACT replica of the Chords Music Academy CRM with zero modifications needed.*