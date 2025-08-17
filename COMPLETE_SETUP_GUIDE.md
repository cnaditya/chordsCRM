# 🎵 Chords Music Academy CRM - Complete Setup Guide

## Overview
A complete Student Management System for music academies with enterprise-grade UI, biometric attendance, payment processing, and WhatsApp notifications.

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
Template ID: 3004 (fees_reminder_new)
Sender ID: CHORDS
Category: MARKETING
Variables: Var1|Var2|Var3 (student_name|plan|due_date)
```

## 🗄️ Database Structure
**SQLite Database:** `chords_crm.db` (auto-created)

### Tables:
1. **students** - Student information
2. **attendance** - Daily attendance records  
3. **payments** - Payment history
4. **allowed_ips** - IP management (disabled)

## 🎨 UI/UX Features
- **Enterprise Design:** Modern blue gradient theme
- **Responsive Layout:** Works on desktop, tablet, mobile
- **Professional Typography:** Inter font family
- **Card-based Navigation:** Hover effects and animations
- **Color-coded Metrics:** Status indicators

## 📋 Core Features

### Student Management
- ✅ Student registration with all details
- ✅ Edit student information
- ✅ Delete students (with confirmation)
- ✅ Instrument selection (9 instruments)
- ✅ International mobile number support

### Attendance System
- ✅ Manual attendance marking
- ✅ Biometric fingerprint enrollment
- ✅ Fingerprint-based attendance
- ✅ Attendance reports

### Payment Processing
- ✅ Fee collection with receipt generation
- ✅ Email receipt sending
- ✅ Payment plans (1M, 3M, 6M, 12M)
- ✅ Due date management
- ✅ Payment history tracking

### Communication
- ✅ WhatsApp reminders for overdue payments
- ✅ Email receipts with professional template
- ✅ Due alerts (next 3 days + overdue)

### Reports & Analytics
- ✅ Dashboard with KPIs
- ✅ Student list with filters
- ✅ Excel export functionality
- ✅ Attendance summary

## 🔧 Hardware Integration

### Biometric Scanner (Mantra MFS100)
**Files:** `mantra_simple.py`, `biometric.py`
```python
# Scanner connection and fingerprint enrollment
# Supports Windows/Linux drivers
# Auto-enrollment with student ID mapping
```

## 🌐 Deployment Options

### Local Deployment
```bash
cd chordsCRM
streamlit run app.py --server.address 0.0.0.0
# Access: http://192.168.0.X:8501 (office network)
```

### Cloud Deployment (Streamlit Cloud)
1. Push code to GitHub
2. Connect to https://share.streamlit.io
3. Deploy from repository
4. Auto-updates on git push

### Custom Server Deployment
```bash
# AWS/DigitalOcean/VPS
pip install streamlit pandas requests openpyxl
streamlit run app.py --server.port 8501
```

## 📱 Mobile Number Formats Supported
```
Indian: 7702031818 (auto-adds 91)
Indian with code: 917702031818
International: +1234567890, +447123456789
Any country code (10-15 digits)
```

## 🎯 Default Data

### Instruments Available
- 🎹 Keyboard/Piano
- 🎸 Guitar  
- 🥁 Drums
- 🎻 Violin
- 🪈 Flute
- 🎤 Vocals (Carnatic/Hindustani/Western)

### Payment Plans
- 1 Month - 8 classes (30 days)
- 3 Month - 24 classes (90 days)  
- 6 Month - 48 classes (180 days)
- 12 Month - 96 classes (365 days)

### Contact Information
```
Phone: +91-7981585309
Website: www.chordsmusicacademy.in
Email: chords.music.academy@gmail.com
```

## 🔒 Security Features
- ✅ Login-based access control
- ✅ Session management
- ✅ HTTPS encryption (cloud deployment)
- ✅ Input validation and sanitization
- ✅ SQL injection protection

## 🛠️ Customization

### Change Login Credentials
**File:** `app.py` (line ~180)
```python
if username == "admin" and password == "admin1":
    # Change these values
```

### Update Contact Information
**File:** `sms_email.py`
```python
# Update phone, email, website in templates
```

### Modify UI Colors
**File:** `style.py`
```python
# Change gradient colors, themes, fonts
```

### Add New Instruments
**File:** `style.py`
```python
def get_instrument_emoji(instrument):
    # Add new instruments here
```

## 📊 File Structure
```
chordsCRM/
├── app.py                 # Main application
├── database.py           # Database operations
├── style.py              # UI/UX styling
├── sms_email.py          # Communication
├── mantra_simple.py      # Biometric integration
├── requirements.txt      # Dependencies
├── chords_crm.db        # SQLite database
└── README.md            # Documentation
```

## 🚨 Troubleshooting

### Common Issues:
1. **"streamlit command not found"**
   ```bash
   python -m streamlit run app.py
   ```

2. **WhatsApp not sending**
   - Check API key validity
   - Verify template approval
   - Confirm mobile number format

3. **Email not sending**
   - Check Gmail app password
   - Verify SMTP settings
   - Check internet connection

4. **Biometric not working**
   - Install Mantra drivers
   - Check USB connection
   - Run as administrator

## 📞 Support
- **Developer:** Aaditya CN
- **Email:** chords.music.academy@gmail.com
- **Phone:** +91-7981585309

## 🎵 Ready to Use!
Your complete music academy management system is ready. All features are pre-configured and working out of the box!

---
*Built with ❤️ for Chords Music Academy*