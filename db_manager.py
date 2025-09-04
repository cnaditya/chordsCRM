#!/usr/bin/env python3
"""
Database Management Utility for Chords Music Academy CRM
Provides tools for database maintenance, backup, and monitoring
"""

import sqlite3
import os
import shutil
from datetime import datetime
import argparse

def backup_database(db_path='chords_crm.db', backup_dir='backups'):
    """Create a timestamped backup of the database"""
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found!")
        return None
    
    # Create backup directory if it doesn't exist
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Create timestamped backup
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"chords_crm_backup_{timestamp}.db"
    backup_path = os.path.join(backup_dir, backup_name)
    
    shutil.copy2(db_path, backup_path)
    
    print(f"Database backed up to: {backup_path}")
    print(f"Backup size: {os.path.getsize(backup_path)} bytes")
    
    return backup_path

def show_database_info(db_path='chords_crm.db'):
    """Display comprehensive database information"""
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("="*60)
    print("CHORDS MUSIC ACADEMY CRM - DATABASE INFO")
    print("="*60)
    
    # Basic info
    print(f"Database Path: {os.path.abspath(db_path)}")
    print(f"Database Size: {os.path.getsize(db_path):,} bytes")
    print(f"Last Modified: {datetime.fromtimestamp(os.path.getmtime(db_path))}")
    
    # Table information
    print("\nTABLE INFORMATION:")
    print("-" * 40)
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    
    total_records = 0
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        total_records += count
        
        # Get table schema
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        print(f"{table_name:20} | {count:8,} records | {len(columns):2} columns")
    
    print(f"{'TOTAL':20} | {total_records:8,} records")
    
    # Recent activity
    print("\nRECENT ACTIVITY:")
    print("-" * 40)
    
    # Recent students
    try:
        cursor.execute("SELECT COUNT(*) FROM students WHERE date(created_at) = date('now')")
        today_students = cursor.fetchone()[0]
        print(f"Students added today: {today_students}")
    except:
        pass
    
    # Recent attendance
    try:
        cursor.execute("SELECT COUNT(*) FROM attendance WHERE date = date('now')")
        today_attendance = cursor.fetchone()[0]
        print(f"Attendance marked today: {today_attendance}")
    except:
        pass
    
    # Recent payments
    try:
        cursor.execute("SELECT COUNT(*) FROM payments WHERE date(payment_date) = date('now')")
        today_payments = cursor.fetchone()[0]
        print(f"Payments received today: {today_payments}")
    except:
        pass
    
    # System health
    print("\nSYSTEM HEALTH:")
    print("-" * 40)
    
    # Check for expired students
    try:
        cursor.execute("SELECT COUNT(*) FROM students WHERE expiry_date < date('now')")
        expired_count = cursor.fetchone()[0]
        print(f"Expired students: {expired_count}")
    except:
        pass
    
    # Check database integrity
    cursor.execute("PRAGMA integrity_check")
    integrity = cursor.fetchone()[0]
    print(f"Database integrity: {integrity}")
    
    conn.close()

def cleanup_old_backups(backup_dir='backups', keep_days=30):
    """Remove backup files older than specified days"""
    if not os.path.exists(backup_dir):
        print("No backup directory found.")
        return
    
    import time
    
    current_time = time.time()
    cutoff_time = current_time - (keep_days * 24 * 60 * 60)
    
    removed_count = 0
    total_size_removed = 0
    
    for filename in os.listdir(backup_dir):
        if filename.startswith('chords_crm_backup_') and filename.endswith('.db'):
            file_path = os.path.join(backup_dir, filename)
            file_time = os.path.getmtime(file_path)
            
            if file_time < cutoff_time:
                file_size = os.path.getsize(file_path)
                os.remove(file_path)
                removed_count += 1
                total_size_removed += file_size
                print(f"Removed old backup: {filename}")
    
    if removed_count > 0:
        print(f"Cleanup complete: {removed_count} files removed, {total_size_removed:,} bytes freed")
    else:
        print("No old backups to remove.")

def optimize_database(db_path='chords_crm.db'):
    """Optimize database performance"""
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found!")
        return
    
    print("Optimizing database...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get size before optimization
    size_before = os.path.getsize(db_path)
    
    # Run optimization commands
    cursor.execute("VACUUM")
    cursor.execute("ANALYZE")
    cursor.execute("REINDEX")
    
    conn.commit()
    conn.close()
    
    # Get size after optimization
    size_after = os.path.getsize(db_path)
    size_saved = size_before - size_after
    
    print(f"Database optimization complete!")
    print(f"Size before: {size_before:,} bytes")
    print(f"Size after:  {size_after:,} bytes")
    print(f"Space saved: {size_saved:,} bytes ({size_saved/size_before*100:.1f}%)")

def export_data(db_path='chords_crm.db', export_dir='exports'):
    """Export data to CSV files"""
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found!")
        return
    
    import csv
    
    # Create export directory
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Tables to export
    tables = ['students', 'attendance', 'payments', 'whatsapp_logs', 'email_logs']
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    for table in tables:
        try:
            cursor.execute(f"SELECT * FROM {table}")
            data = cursor.fetchall()
            
            if data:
                # Get column names
                cursor.execute(f"PRAGMA table_info({table})")
                columns = [col[1] for col in cursor.fetchall()]
                
                # Export to CSV
                csv_path = os.path.join(export_dir, f"{table}_{timestamp}.csv")
                
                with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(columns)  # Header
                    writer.writerows(data)    # Data
                
                print(f"Exported {table}: {len(data)} records -> {csv_path}")
            else:
                print(f"No data in {table} table")
                
        except Exception as e:
            print(f"Error exporting {table}: {e}")
    
    conn.close()

def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description='Chords Music Academy CRM Database Manager')
    parser.add_argument('action', choices=['info', 'backup', 'cleanup', 'optimize', 'export'], 
                       help='Action to perform')
    parser.add_argument('--db', default='chords_crm.db', help='Database file path')
    parser.add_argument('--backup-dir', default='backups', help='Backup directory')
    parser.add_argument('--export-dir', default='exports', help='Export directory')
    parser.add_argument('--keep-days', type=int, default=30, help='Days to keep backups')
    
    args = parser.parse_args()
    
    if args.action == 'info':
        show_database_info(args.db)
    elif args.action == 'backup':
        backup_database(args.db, args.backup_dir)
    elif args.action == 'cleanup':
        cleanup_old_backups(args.backup_dir, args.keep_days)
    elif args.action == 'optimize':
        optimize_database(args.db)
    elif args.action == 'export':
        export_data(args.db, args.export_dir)

if __name__ == "__main__":
    # If no arguments provided, show info by default
    import sys
    if len(sys.argv) == 1:
        show_database_info()
    else:
        main()