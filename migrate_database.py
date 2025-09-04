#!/usr/bin/env python3
"""
Database Migration Script for Chords Music Academy CRM
Migrates existing data from old database structure to new enhanced structure
"""

import sqlite3
import os
from datetime import datetime

def migrate_existing_data():
    """Migrate data from backup to new database structure"""
    
    # Find the most recent backup file
    backup_files = [f for f in os.listdir('.') if f.startswith('chords_crm_backup_') and f.endswith('.db')]
    
    if not backup_files:
        print("No backup database found. Migration not needed.")
        return
    
    # Get the most recent backup
    backup_file = sorted(backup_files)[-1]
    print(f"Migrating data from: {backup_file}")
    
    # Connect to both databases
    old_conn = sqlite3.connect(backup_file)
    new_conn = sqlite3.connect('chords_crm.db')
    
    old_cursor = old_conn.cursor()
    new_cursor = new_conn.cursor()
    
    try:
        # Migrate students
        print("Migrating students...")
        old_cursor.execute('SELECT * FROM students')
        old_students = old_cursor.fetchall()
        
        for student in old_students:
            # Map old structure to new structure
            # Adjust indices based on your old table structure
            try:
                new_cursor.execute('''
                    INSERT OR IGNORE INTO students 
                    (student_id, full_name, age, mobile, email, date_of_birth, sex, 
                     instrument, class_plan, total_classes, start_date, expiry_date, 
                     status, classes_completed, extra_classes, first_class_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', student[1:17])  # Adjust slice based on your structure
                
            except Exception as e:
                print(f"Error migrating student {student[1]}: {e}")
        
        # Migrate attendance
        print("Migrating attendance...")
        old_cursor.execute('SELECT * FROM attendance')
        old_attendance = old_cursor.fetchall()
        
        for att in old_attendance:
            try:
                new_cursor.execute('''
                    INSERT OR IGNORE INTO attendance 
                    (student_id, date, time, attendance_type)
                    VALUES (?, ?, ?, ?)
                ''', (att[1], att[2], att[3], 'Regular'))
                
            except Exception as e:
                print(f"Error migrating attendance: {e}")
        
        # Migrate payments
        print("Migrating payments...")
        old_cursor.execute('SELECT * FROM payments')
        old_payments = old_cursor.fetchall()
        
        for payment in old_payments:
            try:
                new_cursor.execute('''
                    INSERT OR IGNORE INTO payments 
                    (student_id, amount, payment_date, receipt_number, notes, next_due_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', payment[1:7])  # Adjust based on your structure
                
            except Exception as e:
                print(f"Error migrating payment: {e}")
        
        # Migrate allowed IPs if they exist
        try:
            old_cursor.execute('SELECT * FROM allowed_ips')
            old_ips = old_cursor.fetchall()
            
            for ip in old_ips:
                new_cursor.execute('''
                    INSERT OR IGNORE INTO allowed_ips 
                    (ip_address, description, added_date)
                    VALUES (?, ?, ?)
                ''', (ip[1], ip[2], ip[3]))
        except:
            print("No allowed_ips table in old database")
        
        new_conn.commit()
        
        # Get migration stats
        new_cursor.execute('SELECT COUNT(*) FROM students')
        student_count = new_cursor.fetchone()[0]
        
        new_cursor.execute('SELECT COUNT(*) FROM attendance')
        attendance_count = new_cursor.fetchone()[0]
        
        new_cursor.execute('SELECT COUNT(*) FROM payments')
        payment_count = new_cursor.fetchone()[0]
        
        print(f"\nMigration completed successfully!")
        print(f"Migrated {student_count} students")
        print(f"Migrated {attendance_count} attendance records")
        print(f"Migrated {payment_count} payment records")
        
    except Exception as e:
        print(f"Migration error: {e}")
        new_conn.rollback()
    
    finally:
        old_conn.close()
        new_conn.close()

def verify_migration():
    """Verify migration was successful"""
    conn = sqlite3.connect('chords_crm.db')
    cursor = conn.cursor()
    
    print("\n" + "="*50)
    print("Migration Verification")
    print("="*50)
    
    # Check each table
    tables = ['students', 'attendance', 'payments', 'packages', 'instruments', 
              'system_settings', 'allowed_ips']
    
    for table in tables:
        try:
            cursor.execute(f'SELECT COUNT(*) FROM {table}')
            count = cursor.fetchone()[0]
            print(f"{table}: {count} records")
        except Exception as e:
            print(f"{table}: Error - {e}")
    
    conn.close()

def main():
    """Main migration function"""
    print("="*50)
    print("Chords Music Academy CRM - Database Migration")
    print("="*50)
    
    if not os.path.exists('chords_crm.db'):
        print("New database not found. Please run create_database.py first.")
        return
    
    migrate_existing_data()
    verify_migration()
    
    print("\n" + "="*50)
    print("Migration completed!")
    print("="*50)
    print("Your data has been migrated to the new database structure.")
    print("The old database has been preserved as a backup.")

if __name__ == "__main__":
    main()