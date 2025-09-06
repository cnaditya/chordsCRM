# Chords Music Academy CRM - Complete Technical Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Technical Architecture](#technical-architecture)
3. [Database Structure](#database-structure)
4. [API Integrations](#api-integrations)
5. [WhatsApp Templates](#whatsapp-templates)
6. [Email Configuration](#email-configuration)
7. [Payment Processing](#payment-processing)
8. [File Structure](#file-structure)
9. [Deployment Configuration](#deployment-configuration)
10. [Key Business Logic](#key-business-logic)
11. [Troubleshooting Guide](#troubleshooting-guide)
12. [Future Enhancement Guidelines](#future-enhancement-guidelines)

---

## System Overview

### Business Purpose
- **Academy Name**: Chords Music Academy
- **Primary Function**: Student management, fee collection, payment tracking, automated reminders
- **Target Users**: Music academy administrators, students
- **Key Features**: Student registration, payment processing, WhatsApp/Email notifications, due date tracking

### Core Modules
1. **Student Management**: Registration, profile management, course assignment
2. **Payment Processing**: Fee collection, installment tracking, receipt generation
3. **Communication**: WhatsApp templates, email receipts, automated reminders
4. **Analytics**: Payment overview, due alerts, student statistics
5. **Database Management**: SQLite with migration tools

---

## Technical Architecture

### Technology Stack
- **Frontend**: Streamlit (Python web framework)
- **Backend**: Python 3.x
- **Database**: SQLite (chords_crm.db)
- **APIs**: Fast2SMS (WhatsApp/SMS), Gmail SMTP (Email)
- **Deployment**: Streamlit Cloud
- **Version Control**: Git/GitHub

### Core Dependencies
```python
streamlit
pandas
sqlite3
requests
smtplib
datetime
uuid
```

---

## Database Structure

### Primary Tables

#### 1. students_enhanced
```sql
CREATE TABLE students_enhanced (
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
);
```

#### 2. payments
```sql
CREATE TABLE payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT,
    amount REAL,
    payment_date TEXT,
    receipt_number TEXT UNIQUE,
    payment_method TEXT DEFAULT 'Cash',
    notes TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students_enhanced (student_id)
);
```

#### 3. instruments
```sql
CREATE TABLE instruments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);
```

#### 4. plans
```sql
CREATE TABLE plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    amount REAL NOT NULL,
    duration_months INTEGER DEFAULT 1
);
```

### Default Data
```sql
-- Default Instruments
INSERT INTO instruments (name) VALUES 
('Piano/Keyboard'), ('Guitar'), ('Violin'), ('Drums'), 
('Vocals'), ('Flute'), ('Saxophone'), ('Ukulele');

-- Default Plans
INSERT INTO plans (name, amount, duration_months) VALUES
('1 Month - 4', 2000, 1), ('1 Month - 8', 3500, 1),
('3 Months - 4', 5500, 3), ('3 Months - 8', 9500, 3),
('6 Months - 4', 10000, 6), ('6 Months - 8', 18000, 6),
('1 Year - 4', 18000, 12), ('1 Year - 8', 32000, 12);
```

---

## API Integrations

### Fast2SMS Configuration
```python
FAST2SMS_API_KEY = "uC9zfouowPaNrHpOtk5hnVSYiSE9oiihlA7Lld1tBKd49RuUdQusN45x0oPX"
BASE_URL = "https://www.fast2sms.com/dev/whatsapp"
REGISTERED_SENDER = "7981585309"  # Business registered number
```

#### API Parameters
```python
params = {
    "authorization": FAST2SMS_API_KEY,
    "message_id": template_id,
    "numbers": mobile_number,
    "variables_values": "Var1|Var2|Var3"  # Pipe separated
}
```

#### Mobile Number Formatting Rules
1. Remove all spaces, dashes, brackets
2. Remove leading zero if present (07702031818 → 7702031818)
3. Add country code if 10 digits (7702031818 → 917702031818)
4. WhatsApp delivery FROM registered number TO any recipient

---

## WhatsApp Templates

### Template 5170 - Fee Reminder (3 variables)
```
BODY: Hi {Var1}, Your {Var2} package expires on {Var3}.

💰 Payment Options:
📱 UPI: 7702031818 (Any UPI app)

🏦 Bank Transfer:
A/c: 20115230403
IFSC: SBIN0015780
Name: Chippada Naga Aditya Ganesh
Bank: State Bank of India

Thank you - Chords Music Academy
BUTTON: Call Us (PHONE_NUMBER) - +917981585309
```
**Variables**: Student Name | Package Plan | Expiry Date (DD-MM-YYYY)

### Template 5171 - Payment Receipt (6 variables)
```
BODY: Dear {Var1}, 

Thank you for your payment to Chords Music Academy! 🎵

💰 Payment Details:
- Amount: ₹{Var2}
- Receipt No: {Var3}
- Package: {Var4}
- Payment Date: {Var5}

{Var6}

🎶 Keep practicing and let your musical journey flourish!
BUTTON: Call us (PHONE_NUMBER) - +917981585309
```
**Variables**: Student Name | Amount | Receipt No | Package | Payment Date | Next Due Info

### Template 5209 - Installment Reminder (5 variables)
```
BODY: Dear {Var1},

INSTALLMENT REMINDER
Amount: ₹{Var2} due on {Var3}
Package: {Var4} expires {Var5}

💰 Payment Options:
📱 UPI: 7702031818 (Any UPI app)

🏦 Bank Transfer:
A/c: 20115230403
IFSC: SBIN0015780
Name: Chippada Naga Aditya Ganesh
Bank: State Bank of India

Thank you - Chords Music Academy
BUTTON: Call us (PHONE_NUMBER) - +917981585309
```
**Variables**: Student Name | Pending Amount | Due Date | Package Plan | Package End Date

---

## Email Configuration

### Gmail SMTP Settings
```python
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "chords.music.academy@gmail.com"
APP_PASSWORD = "xdiu rhua fhpc zwrk"  # Gmail App Password
```

### Email Receipt Template Structure
```python
subject = "Chords Music Academy - Payment Receipt & Next Due Date"

# Key sections:
# 1. Receipt Details (Receipt No, Student Info, Course Details)
# 2. Payment Summary (Amount, Date, Method, Balance)
# 3. Next Due Information (Based on payment status)
# 4. Contact Information
```

---

## Payment Processing

### Payment Status Types
1. **"Fully Paid - No Dues"**: Complete package payment, no remaining balance
2. **"Installment Payment"**: Partial payment with remaining balance
3. **"Active"**: Default status for ongoing students

### Balance Calculation Logic
```python
# For installment payments
remaining_balance = total_package_amount - total_paid_amount

# Next due date calculation
if installment_payment:
    next_due = current_date + installment_frequency
else:
    next_due = package_expiry_date

# Renewal date logic
renewal_date = package_expiry_date  # Always use package expiry
```

### Receipt Number Generation
```python
# Format: CMA + 5-digit sequential number
# Example: CMA00001, CMA00002, etc.
def generate_receipt_number():
    last_receipt = get_last_receipt_from_db()
    next_number = int(last_receipt[3:]) + 1 if last_receipt else 1
    return f"CMA{next_number:05d}"
```

---

## File Structure

```
chords_crm/
├── app.py                    # Main Streamlit application
├── sms_email.py             # WhatsApp/Email functions
├── create_database.py       # Database initialization
├── database_enhanced.py     # Database operations
├── migrate_database.py      # Data migration tools
├── db_manager.py           # Database maintenance
├── chords_crm.db           # SQLite database file
├── requirements.txt        # Python dependencies
├── .streamlit/
│   └── config.toml         # Streamlit configuration
└── CRM_COMPLETE_DOCUMENTATION.md
```

### Key Files Description

#### app.py - Main Application
- Streamlit interface with multiple pages
- Student management (Add, Edit, View)
- Payment processing with combined buttons
- Due alerts and payment overview
- DataFrame operations with 19-column structure

#### sms_email.py - Communication Module
- WhatsApp template functions (5170, 5171, 5209)
- Email receipt generation
- Mobile number cleaning and formatting
- Error handling and debugging

#### Database Files
- **create_database.py**: Fresh database setup with all tables
- **database_enhanced.py**: CRUD operations with error handling
- **migrate_database.py**: Data migration from old to new structure
- **db_manager.py**: Maintenance and monitoring utilities

---

## Deployment Configuration

### Streamlit Cloud Setup
1. **Repository**: GitHub repository with all files
2. **Database Persistence**: chords_crm.db must be in version control
3. **Environment**: Python 3.9+
4. **Memory**: Standard Streamlit Cloud resources

### Critical Deployment Requirements
```python
# requirements.txt
streamlit>=1.28.0
pandas>=1.5.0
requests>=2.28.0

# .streamlit/config.toml
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
```

### Git Workflow
```bash
git add .
git commit -m "Description of changes"
git push origin main
# Auto-deploys to Streamlit Cloud
```

---

## Key Business Logic

### Student Registration Flow
1. Generate unique student ID (format: CMA + timestamp)
2. Validate mobile number and email
3. Calculate package expiry date based on plan duration
4. Set initial payment status and due dates
5. Store in students_enhanced table

### Payment Processing Flow
1. **Input Validation**: Amount, student selection, payment method
2. **Balance Calculation**: Update remaining balance and total paid
3. **Receipt Generation**: Create unique receipt number
4. **Database Updates**: Update student record and create payment entry
5. **Communication**: Send WhatsApp receipt and email simultaneously
6. **Status Updates**: Update payment status based on remaining balance

### Due Date Management
```python
# Package expiry (for fully paid students)
expiry_date = start_date + package_duration

# Installment due date (for partial payments)
next_due = last_payment_date + installment_frequency

# Renewal date (always package expiry)
renewal_date = package_expiry_date
```

### Template Selection Logic
```python
if remaining_balance > 0:
    # Use installment reminder (5209)
    send_whatsapp_installment_reminder()
else:
    # Use fee reminder (5170) 
    send_whatsapp_reminder()
```

---

## Troubleshooting Guide

### Common Issues and Solutions

#### 1. WhatsApp Delivery Failures
**Problem**: Messages not delivered
**Solutions**:
- Check mobile number format (remove leading zeros)
- Verify sender number is registered (7981585309)
- Ensure template ID exists and is approved
- Check API key validity

#### 2. Database Persistence Issues
**Problem**: Data disappears after deployment
**Solutions**:
- Ensure chords_crm.db is in Git repository
- Check file is not in .gitignore
- Verify database file permissions

#### 3. DataFrame Column Errors
**Problem**: Column mismatch errors
**Solutions**:
- Verify database has 19 columns in correct order
- Check column names match exactly
- Run database migration if needed

#### 4. Date Parsing Errors
**Problem**: Date format conversion failures
**Solutions**:
```python
try:
    date_obj = datetime.strptime(str(date_str), '%Y-%m-%d')
    formatted_date = date_obj.strftime('%d-%m-%Y')
except:
    formatted_date = str(date_str)  # Fallback
```

#### 5. Streamlit Button Key Conflicts
**Problem**: Duplicate button key errors
**Solutions**:
- Add unique keys to all buttons: `key=f"btn_{unique_identifier}"`
- Use student ID or timestamp for uniqueness

---

## Future Enhancement Guidelines

### Scalability Improvements
1. **Database Migration**: SQLite → PostgreSQL for production
2. **Authentication**: Add user login and role-based access
3. **Multi-tenancy**: Support multiple academies
4. **API Rate Limiting**: Implement request throttling

### Feature Enhancements
1. **Advanced Reporting**: Revenue analytics, student retention
2. **Bulk Operations**: Mass SMS/email campaigns
3. **Calendar Integration**: Class scheduling and reminders
4. **Mobile App**: React Native or Flutter app
5. **Payment Gateway**: Razorpay/Stripe integration

### Technical Improvements
1. **Error Logging**: Comprehensive logging system
2. **Backup System**: Automated database backups
3. **Performance Optimization**: Query optimization and caching
4. **Security**: Data encryption and secure API handling

### Business Logic Extensions
1. **Attendance Tracking**: Class attendance management
2. **Instructor Management**: Teacher assignment and scheduling
3. **Inventory Management**: Instrument and equipment tracking
4. **Student Progress**: Skill level tracking and assessments

---

## Bank Details Reference

### Payment Information
- **UPI ID**: 7702031818
- **Account Number**: 20115230403
- **IFSC Code**: SBIN0015780
- **Account Holder**: Chippada Naga Aditya Ganesh
- **Bank**: State Bank of India
- **Contact**: +91-7981585309

---

## API Keys and Credentials

### Fast2SMS
- **API Key**: uC9zfouowPaNrHpOtk5hnVSYiSE9oiihlA7Lld1tBKd49RuUdQusN45x0oPX
- **Registered Number**: 7981585309
- **Template IDs**: 5170 (Fee Reminder), 5171 (Receipt), 5209 (Installment)

### Gmail SMTP
- **Email**: chords.music.academy@gmail.com
- **App Password**: xdiu rhua fhpc zwrk
- **SMTP**: smtp.gmail.com:587

---

## Development Best Practices

### Code Organization
1. **Separation of Concerns**: Keep database, communication, and UI logic separate
2. **Error Handling**: Comprehensive try-catch blocks with user-friendly messages
3. **Data Validation**: Input validation at all entry points
4. **Documentation**: Inline comments for complex business logic

### Testing Strategy
1. **Unit Tests**: Test individual functions with mock data
2. **Integration Tests**: Test API integrations with test accounts
3. **User Acceptance Testing**: Test complete workflows with real data
4. **Performance Testing**: Load testing with large datasets

### Security Considerations
1. **API Key Management**: Store sensitive keys securely
2. **Input Sanitization**: Prevent SQL injection and XSS
3. **Data Privacy**: Comply with data protection regulations
4. **Access Control**: Implement proper authentication and authorization

---

## Conclusion

This CRM system represents a complete solution for music academy management with integrated communication, payment processing, and student tracking. The modular architecture allows for easy maintenance and future enhancements while maintaining data integrity and user experience.

**Key Success Factors**:
- Robust database design with proper relationships
- Reliable API integrations with error handling
- User-friendly interface with combined operations
- Comprehensive documentation for maintenance
- Scalable architecture for future growth

**Maintenance Schedule**:
- Weekly: Database backup and performance monitoring
- Monthly: API key rotation and security updates
- Quarterly: Feature updates and user feedback integration
- Annually: Full system audit and technology stack review

---

*Document Version: 1.0*  
*Last Updated: December 2024*  
*Created by: Amazon Q Developer*  
*For: Chords Music Academy CRM System*