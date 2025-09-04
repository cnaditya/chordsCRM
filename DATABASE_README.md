# Chords Music Academy CRM - Database Documentation

## Overview
This document describes the database structure and management for the Chords Music Academy CRM system.

## Database Structure

### Core Tables

#### 1. Students Table
Stores all student information and enrollment details.
```sql
- id: Primary key (auto-increment)
- student_id: Unique student identifier (CHORDS001, CHORDS002, etc.)
- full_name: Student's full name
- age: Student's age
- mobile: Contact number
- email: Email address
- date_of_birth: Birth date
- sex: Gender
- instrument: Instrument being learned
- class_plan: Package selected
- total_classes: Total classes in package
- start_date: Course start date
- expiry_date: Package expiry date
- status: Active/Inactive status
- classes_completed: Number of classes attended
- extra_classes: Additional classes beyond package
- first_class_date: Date of first attendance
- created_at: Record creation timestamp
- updated_at: Last update timestamp
```

#### 2. Attendance Table
Tracks student attendance for each class.
```sql
- id: Primary key
- student_id: Reference to student
- date: Attendance date
- time: Attendance time
- attendance_type: Regular/Extra/Makeup
- notes: Additional notes
- created_at: Record timestamp
```

#### 3. Payments Table
Records all fee payments and transactions.
```sql
- id: Primary key
- student_id: Reference to student
- amount: Payment amount
- payment_date: Date of payment
- receipt_number: Unique receipt number (CMA00001, etc.)
- payment_method: Cash/UPI/Card
- notes: Payment notes
- next_due_date: Next payment due date
- payment_status: Completed/Pending/Failed
- created_at: Record timestamp
```

#### 4. Packages Table
Defines available course packages.
```sql
- id: Primary key
- package_name: Package name (e.g., "1 Month - 8")
- total_classes: Number of classes
- duration_days: Package duration in days
- price: Package price
- description: Package description
- is_active: Active/Inactive status
- created_at: Creation timestamp
```

#### 5. Instruments Table
Lists available instruments.
```sql
- id: Primary key
- instrument_name: Instrument name
- emoji: Display emoji
- is_active: Active/Inactive status
- created_at: Creation timestamp
```

### Communication Tables

#### 6. WhatsApp Logs Table
Tracks WhatsApp message history.
```sql
- id: Primary key
- student_id: Reference to student
- mobile_number: Recipient number
- message_type: Reminder/Receipt/General
- template_id: WhatsApp template ID
- message_content: Message text
- status: Success/Failed
- response_data: API response
- sent_at: Send timestamp
```

#### 7. Email Logs Table
Tracks email communication history.
```sql
- id: Primary key
- student_id: Reference to student
- email_address: Recipient email
- subject: Email subject
- message_type: Receipt/Reminder/General
- status: Success/Failed
- error_message: Error details if failed
- sent_at: Send timestamp
```

### System Tables

#### 8. System Settings Table
Stores application configuration.
```sql
- id: Primary key
- setting_key: Setting name
- setting_value: Setting value
- description: Setting description
- updated_at: Last update timestamp
```

#### 9. Allowed IPs Table
Manages IP-based access control.
```sql
- id: Primary key
- ip_address: Allowed IP address
- description: IP description
- is_active: Active/Inactive status
- added_date: Addition timestamp
```

## Database Management

### 1. Database Creation
```bash
# Create new database with complete structure
python3 create_database.py
```

### 2. Data Migration
```bash
# Migrate data from old database structure
python3 migrate_database.py
```

### 3. Database Management
```bash
# Show database information
python3 db_manager.py info

# Create backup
python3 db_manager.py backup

# Optimize database
python3 db_manager.py optimize

# Export data to CSV
python3 db_manager.py export

# Cleanup old backups
python3 db_manager.py cleanup
```

### 4. Version Control
The database file (`chords_crm.db`) is included in Git to ensure data persistence across deployments.

```bash
# Add database to Git
git add chords_crm.db

# Commit changes
git commit -m "Update database"

# Push to repository
git push
```

## Default Data

### Packages
- No Package (0 classes, ₹0)
- 1 Month - 8 (8 classes, ₹4,000)
- 3 Month - 24 (24 classes, ₹10,800)
- 6 Month - 48 (48 classes, ₹20,400)
- 12 Month - 96 (96 classes, ₹38,400)

### Instruments
- Keyboard 🎹
- Piano 🎹
- Guitar 🎸
- Drums 🥁
- Violin 🎻
- Flute 🪈
- Carnatic Vocals 🎤
- Hindustani Vocals 🎤
- Western Vocals 🎤

### System Settings
- Academy name: "Chords Music Academy"
- Receipt prefix: "CMA"
- WhatsApp templates: 5170 (reminders), 5171 (receipts)
- Business hours: 9:00 AM - 8:00 PM

## Backup Strategy

### Automatic Backups
- Database is automatically backed up before major operations
- Backups are stored in the `backups/` directory
- Old backups are cleaned up after 30 days

### Manual Backups
```bash
# Create manual backup
python3 db_manager.py backup

# Create backup with custom location
python3 db_manager.py backup --backup-dir /path/to/backups
```

## Performance Optimization

### Indexes
The database includes optimized indexes for:
- Student ID lookups
- Mobile number searches
- Instrument filtering
- Date-based queries
- Payment tracking

### Maintenance
```bash
# Optimize database performance
python3 db_manager.py optimize
```

## Security Features

### Data Protection
- Foreign key constraints ensure data integrity
- Proper indexing for fast queries
- Transaction support for data consistency

### Access Control
- IP-based access restrictions
- Session management
- Audit logging for communications

## Troubleshooting

### Common Issues

1. **Database not found**
   ```bash
   python3 create_database.py
   ```

2. **Data migration needed**
   ```bash
   python3 migrate_database.py
   ```

3. **Performance issues**
   ```bash
   python3 db_manager.py optimize
   ```

4. **Backup corruption**
   ```bash
   # Restore from backup
   cp backups/chords_crm_backup_YYYYMMDD_HHMMSS.db chords_crm.db
   ```

### Database Integrity Check
```bash
# Check database health
python3 db_manager.py info
```

## API Integration

### Enhanced Database Module
The `database_enhanced.py` module provides:
- Object-oriented database operations
- Better error handling
- Comprehensive logging
- Type hints for better code quality
- Legacy compatibility with existing code

### Usage Example
```python
from database_enhanced import DatabaseManager

# Initialize database manager
db = DatabaseManager()

# Add student
student_id = db.add_student(
    full_name="John Doe",
    age=25,
    mobile="9876543210",
    email="john@example.com",
    date_of_birth="1998-01-01",
    sex="Male",
    instrument="Guitar",
    class_plan="3 Month - 24",
    start_date="2024-01-01"
)

# Mark attendance
success, message = db.mark_attendance(student_id)

# Add payment
receipt_no = db.add_payment(
    student_id=student_id,
    amount=10800,
    payment_method="UPI Payment",
    notes="Full payment for 3-month package"
)
```

## Deployment Notes

### Streamlit Cloud
- Database file is included in Git repository
- Automatic deployment preserves data
- No additional configuration required

### Local Development
- Database is created automatically on first run
- All data persists between sessions
- Backup and restore capabilities available

---

**Last Updated:** September 4, 2024  
**Database Version:** 1.0  
**CRM Version:** 2.0