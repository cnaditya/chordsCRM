# 🎵 Chords Music Academy CRM - Complete Documentation

## 📋 Overview
A comprehensive Student Management System for music academies with enterprise-grade UI, biometric attendance, flexible payment processing, and dual communication (Email + WhatsApp).

## 🚀 Quick Setup (New Machine)

### 1. Prerequisites
```bash
# Install Python 3.8+
# Download from: https://python.org/downloads

# Install Git
# Download from: https://git-scm.com/downloads
```

### 2. Clone & Setup
```bash
# Clone the repository
git clone https://github.com/cnaditya/chordsCRM.git
cd chordsCRM

# Install dependencies
pip install streamlit pandas requests openpyxl sqlite3

# Run the application
streamlit run app.py
```

### 3. Access URLs
- **Local:** http://localhost:8501
- **Web:** https://share.streamlit.io (search for "chordsCRM")

## 🔐 Login Credentials
```
Username: admin
Password: admin1
```

## 📧 Email Configuration (Gmail SMTP)
**File:** `sms_email.py`
```python
sender_email = "chords.music.academy@gmail.com"
sender_password = "xdiu rhua fhpc zwrk"  # App Password
```

## 📱 WhatsApp/SMS Configuration (Fast2SMS)
**File:** `sms_email.py`
```python
FAST2SMS_API_KEY = "6TDScuetHNniG5F92kswhvrLJx4IAVRjpoZUb1Y83CzBl0WEd7RLDaifTQwBqekSC2vnMz583p4lKsdX"

# Template Details:
Template ID: 3004 (fees_reminder_new) - Overdue Reminders
Template ID: 4587 (payment_receipt) - Payment Receipts
Sender ID: CHORDS
Category: MARKETING
```

### WhatsApp Templates Used:

**Template 3004 (Overdue Reminders):**
```
Dear {{1}}, this is a reminder from Chords Music Academy.

Your fee for {{2}} classes is due on {{3}}. Pay before the due date and get exclusive offers on your next enrollment.

🎶 Let the music continue without interruption!
📞 Contact us at +91 7981585309
```

**Template 4587 (Payment Receipts):**
```
Dear {{1}}, 

Thank you for your payment to Chords Music Academy! 🎵

💰 Payment Details:
- Amount: ₹{{2}}
- Receipt No: {{3}}
- Package: {{4}}
- Payment Date: {{5}}

{{6}}

🎶 Keep practicing and let your musical journey flourish!
📞 Contact us at +91 7981585309
```

## 💰 Fee Structure (Chords Music Academy)
```python
# In app.py - payment_module()
default_package_fees = {
    "1 Month - 8": 4000,      # ₹4,000
    "3 Month - 24": 10800,    # ₹10,800 (10% off)
    "6 Month - 48": 20400,    # ₹20,400 (15% off)
    "12 Month - 96": 38400,   # ₹38,400 (20% off)
    "No Package": 0
}
```

## 🗄️ Database Structure
**SQLite Database:** `chords_crm.db` (auto-created)

### Tables:

**1. students**
```sql
CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT UNIQUE,
    full_name TEXT,
    age INTEGER,
    mobile TEXT,
    email TEXT,
    date_of_birth TEXT,
    sex TEXT,
    instrument TEXT,
    class_plan TEXT,
    total_classes INTEGER,
    start_date TEXT,
    expiry_date TEXT,
    status TEXT DEFAULT 'Active',
    classes_completed INTEGER DEFAULT 0,
    extra_classes INTEGER DEFAULT 0,
    first_class_date TEXT
);
```

**2. attendance**
```sql
CREATE TABLE attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT,
    date TEXT,
    time TEXT,
    FOREIGN KEY (student_id) REFERENCES students (student_id)
);
```

**3. payments**
```sql
CREATE TABLE payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT,
    amount REAL,
    payment_date TEXT,
    receipt_number TEXT,
    notes TEXT,
    next_due_date TEXT,
    FOREIGN KEY (student_id) REFERENCES students (student_id)
);
```

**4. allowed_ips**
```sql
CREATE TABLE allowed_ips (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip_address TEXT UNIQUE,
    description TEXT,
    added_date TEXT
);
```

## 📁 File Structure
```
chordsCRM/
├── app.py                    # Main application (1,400+ lines)
├── database.py              # Database operations
├── style.py                 # UI/UX styling & components
├── sms_email.py             # Email & WhatsApp communication
├── mantra_simple.py         # Biometric integration
├── biometric.py             # Biometric helper functions
├── requirements.txt         # Python dependencies
├── chords_crm.db           # SQLite database (auto-created)
├── COMPLETE_DOCUMENTATION.md # This file
├── COMPLETE_SETUP_GUIDE.md  # Setup guide
└── README.md               # Basic documentation
```

## 🎨 UI/UX Features

### Color Scheme & Design
**File:** `style.py`
```python
# Primary colors
primary_blue = "#3b82f6"
success_green = "#10b981"
warning_orange = "#f59e0b"
purple_accent = "#8b5cf6"

# Background
background_color = "#f8fafc"
```

### Navigation Cards
- **Student Management:** 👥 (Registration, List & Edit)
- **Operations Management:** 📈 (Attendance, Biometric)
- **Financial Management:** 💰 (Payments, Reports)

## 🎵 Core Features

### 1. Student Management
**Registration Flow:**
1. **Student Registration** → Basic details only, "No Package" assigned
2. **Student List & Edit** → Assign packages, auto-calculate expiry dates
3. **Status Logic:**
   - ⚪ No Package (new students)
   - 🟢 Active (valid package)
   - 🔴 Expired (package expired)

### 2. Payment Processing (Flexible Installments)
**Features:**
- ✅ **Payment Summary:** Total Fees, Paid Amount, Pending Amount
- ✅ **Flexible Payments:** Partial or full payments
- ✅ **Installment Tracking:** Next due dates, payment notes
- ✅ **Dual Receipts:** Email + WhatsApp
- ✅ **Bargaining Support:** Editable package fees
- ✅ **Payment Status:** "Installment Payment" or "Fully Paid - No Dues"

**Payment Workflow:**
1. **Search student** or view due/overdue students
2. **Set package fee** (editable for bargaining)
3. **Enter payment amount** (suggests pending amount)
4. **Choose payment status:**
   - Installment → Set next due date
   - Fully Paid → No future dues
5. **Process payment** → Dual receipts sent

### 3. Communication System
**Email Receipts:**
- Professional template with complete details
- Shows package validity vs payment schedule
- Sent via Gmail SMTP

**WhatsApp Integration:**
- **Overdue Reminders:** Template 3004
- **Payment Receipts:** Template 4587
- International mobile number support
- Fast2SMS API integration

### 4. Attendance System
**Manual Attendance:**
- Enter Student ID manually
- Tracks regular classes, extra classes, makeup classes

**Biometric Attendance:**
- Mantra MFS100 scanner integration
- Fingerprint enrollment and scanning
- Automatic attendance marking

### 5. Reports & Analytics
- **Dashboard KPIs:** Total, Active, Expired, Today's Attendance
- **Student Reports:** Filterable, exportable to Excel
- **Due Alerts:** Next 3 days + overdue students
- **Payment Tracking:** Complete payment history

## 🔧 Hardware Integration

### Biometric Scanner (Mantra MFS100)
**Files:** `mantra_simple.py`, `biometric.py`
```python
# Scanner connection
scanner.connect_scanner()
scanner.enroll_fingerprint(student_id)
scanner.scan_fingerprint()
```

## 🌐 Deployment Options

### Local Deployment
```bash
cd chordsCRM
streamlit run app.py --server.address 0.0.0.0
# Access: http://192.168.0.X:8501
```

### Cloud Deployment (Streamlit Cloud)
1. Push code to GitHub: https://github.com/cnaditya/chordsCRM.git
2. Connect to https://share.streamlit.io
3. Deploy from repository
4. Auto-updates on git push

### Custom Server Deployment
```bash
# AWS/DigitalOcean/VPS
pip install streamlit pandas requests openpyxl
streamlit run app.py --server.port 8501
```

## 📱 Mobile Number Support
**International Format Handling:**
```python
# Supported formats:
7702031818          # Indian (auto-adds 91)
917702031818        # Indian with code
+917702031818       # Indian with + and code
+1234567890         # US numbers
+447123456789       # UK numbers
# Any country code (10-15 digits)
```

## 🎯 Default Data & Configuration

### Instruments Available
```python
instruments = [
    "Keyboard", "Piano", "Guitar", "Drums", "Violin", 
    "Flute", "Carnatic Vocals", "Hindustani Vocals", "Western Vocals"
]
```

### Payment Plans
```python
class_plans = {
    "No Package": (0, 0),
    "1 Month - 8": (8, 30), 
    "3 Month - 24": (24, 90), 
    "6 Month - 48": (48, 180), 
    "12 Month - 96": (96, 365)
}
```

### Contact Information
```python
phone = "+91-7981585309"
website = "www.chordsmusicacademy.in"
email = "chords.music.academy@gmail.com"
```

## 🔒 Security Features
- ✅ Login-based access control (admin/admin1)
- ✅ Session management
- ✅ Input validation and sanitization
- ✅ SQL injection protection
- ✅ International mobile number validation

## 🛠️ Customization Guide

### Change Login Credentials
**File:** `app.py` (line ~200)
```python
if username == "admin" and password == "admin1":
    # Change these values
```

### Update Fee Structure
**File:** `app.py` (payment_module function)
```python
default_package_fees = {
    "1 Month - 8": 4000,      # Change amounts here
    "3 Month - 24": 10800,
    # ... etc
}
```

### Update Contact Information
**Files:** `sms_email.py`, WhatsApp templates
```python
# Update phone, email, website in templates
phone = "+91-7981585309"
email = "chords.music.academy@gmail.com"
```

### Add New Instruments
**File:** `style.py`
```python
def get_instrument_emoji(instrument):
    # Add new instruments here
    emoji_map = {
        "Keyboard": "🎹",
        "Piano": "🎹",
        # Add more...
    }
```

### Modify UI Colors
**File:** `style.py`
```python
# Change gradient colors, themes, fonts
primary_color = "#3b82f6"  # Blue
success_color = "#10b981"  # Green
# etc...
```

## 🚨 Troubleshooting

### Common Issues:

**1. "streamlit command not found"**
```bash
python -m streamlit run app.py
```

**2. WhatsApp not sending**
- Check API key validity in Fast2SMS dashboard
- Verify template approval status
- Confirm mobile number format (with country code)
- Check template variable count matches

**3. Email not sending**
- Check Gmail app password (not regular password)
- Verify SMTP settings (smtp.gmail.com:587)
- Check internet connection
- Enable "Less secure app access" if needed

**4. Biometric not working**
- Install Mantra MFS100 drivers
- Check USB connection
- Run application as administrator
- Verify scanner device recognition

**5. Database errors**
- Delete `chords_crm.db` to reset database
- Check file permissions
- Ensure SQLite3 is installed

**6. Student registration validation fails**
- Clear browser cache
- Refresh page (F5)
- Check for JavaScript errors in browser console

## 📊 Performance Considerations

### Database Optimization
- SQLite handles up to 1000+ students efficiently
- Indexes on student_id for faster lookups
- Regular database cleanup recommended

### UI Performance
- Pagination (10 students per page) for large lists
- Search-first approach (no data shown by default)
- Efficient session state management

## 🔄 Backup & Maintenance

### Database Backup
```bash
# Backup database
cp chords_crm.db chords_crm_backup_$(date +%Y%m%d).db

# Restore database
cp chords_crm_backup_20250822.db chords_crm.db
```

### Log Monitoring
- Check Streamlit logs for errors
- Monitor Fast2SMS API usage
- Track email delivery status

## 📈 Future Enhancements

### Potential Additions
- **Student Portal:** Login for students to view progress
- **Teacher Management:** Multiple teacher assignments
- **Advanced Reports:** Revenue analytics, attendance trends
- **Mobile App:** React Native or Flutter app
- **Online Payments:** Razorpay/PayU integration
- **Bulk Operations:** Mass email/WhatsApp sending
- **Calendar Integration:** Class scheduling

## 📞 Support & Contact

**Developer:** Aaditya CN
**Academy:** Chords Music Academy
**Email:** chords.music.academy@gmail.com
**Phone:** +91-7981585309
**GitHub:** https://github.com/cnaditya/chordsCRM

## 🎵 System Summary

**This CRM provides:**
- ✅ **Complete Student Lifecycle Management**
- ✅ **Flexible Payment Processing with Installments**
- ✅ **Dual Communication (Email + WhatsApp)**
- ✅ **Biometric Attendance Integration**
- ✅ **Professional UI/UX Design**
- ✅ **Scalable Architecture (1000+ students)**
- ✅ **Real-world Business Logic**
- ✅ **International Support**

**Ready for production use in any music academy worldwide!**

---
*Built with ❤️ for Chords Music Academy - Complete Documentation v1.0*