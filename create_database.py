#!/usr/bin/env python3
"""
Chords Music Academy CRM - Database Creation Script
Creates and initializes the complete database structure for the CRM system.
"""

import sqlite3
import os
from datetime import datetime

def create_database():
    """Create and initialize the complete database structure"""
    
    # Database file path
    db_path = 'chords_crm.db'
    
    print(f"Creating database: {db_path}")
    
    # Connect to database (creates file if doesn't exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Enable foreign key constraints
    cursor.execute('PRAGMA foreign_keys = ON')
    
    print("Creating tables...")
    
    # 1. Students table - Core student information
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            age INTEGER,
            mobile TEXT NOT NULL,
            email TEXT,
            date_of_birth TEXT,
            sex TEXT,
            instrument TEXT NOT NULL,
            class_plan TEXT DEFAULT 'No Package',
            total_classes INTEGER DEFAULT 0,
            start_date TEXT NOT NULL,
            expiry_date TEXT,
            status TEXT DEFAULT 'Active',
            classes_completed INTEGER DEFAULT 0,
            extra_classes INTEGER DEFAULT 0,
            first_class_date TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 2. Attendance table - Track student attendance
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            attendance_type TEXT DEFAULT 'Regular',
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students (student_id) ON DELETE CASCADE
        )
    ''')
    
    # 3. Payments table - Track fee payments
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            amount REAL NOT NULL,
            payment_date TEXT NOT NULL,
            receipt_number TEXT UNIQUE NOT NULL,
            payment_method TEXT DEFAULT 'Cash Payment',
            notes TEXT,
            next_due_date TEXT,
            payment_status TEXT DEFAULT 'Completed',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students (student_id) ON DELETE CASCADE
        )
    ''')
    
    # 4. Packages table - Define course packages
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS packages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            package_name TEXT UNIQUE NOT NULL,
            total_classes INTEGER NOT NULL,
            duration_days INTEGER NOT NULL,
            price REAL NOT NULL,
            description TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 5. Instruments table - Define available instruments
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS instruments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            instrument_name TEXT UNIQUE NOT NULL,
            emoji TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 6. WhatsApp logs table - Track WhatsApp messages
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS whatsapp_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            mobile_number TEXT NOT NULL,
            message_type TEXT NOT NULL,
            template_id TEXT,
            message_content TEXT,
            status TEXT NOT NULL,
            response_data TEXT,
            sent_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students (student_id) ON DELETE SET NULL
        )
    ''')
    
    # 7. Email logs table - Track email communications
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS email_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            email_address TEXT NOT NULL,
            subject TEXT NOT NULL,
            message_type TEXT NOT NULL,
            status TEXT NOT NULL,
            error_message TEXT,
            sent_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students (student_id) ON DELETE SET NULL
        )
    ''')
    
    # 8. System settings table - Store application settings
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            setting_key TEXT UNIQUE NOT NULL,
            setting_value TEXT,
            description TEXT,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 9. Allowed IPs table - Security management
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS allowed_ips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address TEXT UNIQUE NOT NULL,
            description TEXT,
            is_active BOOLEAN DEFAULT 1,
            added_date TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    print("Inserting default data...")
    
    # Insert default packages
    default_packages = [
        ('No Package', 0, 0, 0, 'No package selected'),
        ('1 Month - 8', 8, 30, 4000, '8 classes in 1 month'),
        ('3 Month - 24', 24, 90, 10800, '24 classes in 3 months (10% discount)'),
        ('6 Month - 48', 48, 180, 20400, '48 classes in 6 months (15% discount)'),
        ('12 Month - 96', 96, 365, 38400, '96 classes in 12 months (20% discount)')
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO packages (package_name, total_classes, duration_days, price, description)
        VALUES (?, ?, ?, ?, ?)
    ''', default_packages)
    
    # Insert default instruments
    default_instruments = [
        ('Keyboard', '🎹'),
        ('Piano', '🎹'),
        ('Guitar', '🎸'),
        ('Drums', '🥁'),
        ('Violin', '🎻'),
        ('Flute', '🪈'),
        ('Carnatic Vocals', '🎤'),
        ('Hindustani Vocals', '🎤'),
        ('Western Vocals', '🎤')
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO instruments (instrument_name, emoji)
        VALUES (?, ?)
    ''', default_instruments)
    
    # Insert default system settings
    default_settings = [
        ('academy_name', 'Chords Music Academy', 'Academy name for receipts and communications'),
        ('fast2sms_api_key', '', 'Fast2SMS API key for WhatsApp and SMS'),
        ('email_sender', 'admin@chordsacademy.com', 'Default sender email address'),
        ('whatsapp_template_reminder', '5170', 'WhatsApp template ID for fee reminders'),
        ('whatsapp_template_receipt', '5171', 'WhatsApp template ID for payment receipts'),
        ('receipt_prefix', 'CMA', 'Prefix for receipt numbers'),
        ('business_hours_start', '09:00', 'Business hours start time'),
        ('business_hours_end', '20:00', 'Business hours end time'),
        ('database_version', '1.0', 'Current database schema version')
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO system_settings (setting_key, setting_value, description)
        VALUES (?, ?, ?)
    ''', default_settings)
    
    # Insert default allowed IPs
    default_ips = [
        ('192.168.0.', 'Local network range'),
        ('127.0.0.1', 'Localhost'),
        ('35.197.92.111', 'Streamlit Cloud Server'),
        ('49.204.30.164', 'Office IP'),
        ('49.204.28.147', 'Home IP')
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO allowed_ips (ip_address, description)
        VALUES (?, ?)
    ''', default_ips)
    
    # Create indexes for better performance
    print("Creating indexes...")
    
    indexes = [
        'CREATE INDEX IF NOT EXISTS idx_students_student_id ON students(student_id)',
        'CREATE INDEX IF NOT EXISTS idx_students_mobile ON students(mobile)',
        'CREATE INDEX IF NOT EXISTS idx_students_instrument ON students(instrument)',
        'CREATE INDEX IF NOT EXISTS idx_students_expiry ON students(expiry_date)',
        'CREATE INDEX IF NOT EXISTS idx_attendance_student_date ON attendance(student_id, date)',
        'CREATE INDEX IF NOT EXISTS idx_payments_student ON payments(student_id)',
        'CREATE INDEX IF NOT EXISTS idx_payments_date ON payments(payment_date)',
        'CREATE INDEX IF NOT EXISTS idx_whatsapp_logs_student ON whatsapp_logs(student_id)',
        'CREATE INDEX IF NOT EXISTS idx_email_logs_student ON email_logs(student_id)'
    ]
    
    for index in indexes:
        cursor.execute(index)
    
    # Commit all changes
    conn.commit()
    
    # Get database info
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print(f"\nDatabase created successfully!")
    print(f"Location: {os.path.abspath(db_path)}")
    print(f"Tables created: {len(tables)}")
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cursor.fetchone()[0]
        print(f"  - {table[0]}: {count} records")
    
    conn.close()
    return db_path

def backup_existing_data():
    """Backup existing database if it exists"""
    if os.path.exists('chords_crm.db'):
        backup_name = f"chords_crm_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        os.rename('chords_crm.db', backup_name)
        print(f"Existing database backed up as: {backup_name}")
        return backup_name
    return None

def main():
    """Main function to create database"""
    print("=" * 50)
    print("Chords Music Academy CRM - Database Setup")
    print("=" * 50)
    
    # Backup existing database
    backup_file = backup_existing_data()
    
    # Create new database
    db_path = create_database()
    
    print("\n" + "=" * 50)
    print("Database setup completed successfully!")
    print("=" * 50)
    
    if backup_file:
        print(f"Previous database backed up as: {backup_file}")
    
    print(f"New database created: {db_path}")
    print("\nNext steps:")
    print("1. Add the database file to Git: git add chords_crm.db")
    print("2. Commit the changes: git commit -m 'Add database file'")
    print("3. Push to repository: git push")
    print("\nThe CRM system is now ready to use!")

if __name__ == "__main__":
    main()