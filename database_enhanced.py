"""
Enhanced Database Module for Chords Music Academy CRM
Provides comprehensive database operations with improved error handling and logging
"""

import sqlite3
import os
from datetime import datetime, timedelta
import re
from typing import Optional, List, Tuple, Dict, Any

class DatabaseManager:
    """Enhanced database manager with comprehensive operations"""
    
    def __init__(self, db_path: str = 'chords_crm.db'):
        self.db_path = db_path
        self.ensure_database_exists()
    
    def ensure_database_exists(self):
        """Ensure database exists and has proper structure"""
        if not os.path.exists(self.db_path):
            print(f"Database not found. Creating new database: {self.db_path}")
            from create_database import create_database
            create_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection with proper configuration"""
        conn = sqlite3.connect(self.db_path)
        conn.execute('PRAGMA foreign_keys = ON')
        return conn
    
    def execute_query(self, query: str, params: tuple = ()) -> List[tuple]:
        """Execute SELECT query and return results"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute INSERT/UPDATE/DELETE query and return affected rows"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount
    
    # Student Management
    def get_next_student_id(self) -> str:
        """Generate next student ID"""
        result = self.execute_query('SELECT student_id FROM students ORDER BY student_id DESC LIMIT 1')
        
        if result:
            last_id = result[0][0]
            try:
                last_number = int(last_id.replace('CHORDS', ''))
                next_number = last_number + 1
            except:
                count = self.execute_query('SELECT COUNT(*) FROM students')[0][0]
                next_number = count + 1
        else:
            next_number = 1
        
        return f"CHORDS{next_number:03d}"
    
    def add_student(self, full_name: str, age: int, mobile: str, email: str, 
                   date_of_birth: str, sex: str, instrument: str, 
                   class_plan: str, start_date: str) -> str:
        """Add new student to database"""
        student_id = self.get_next_student_id()
        
        # Get package details
        package_info = self.get_package_info(class_plan)
        total_classes = package_info['total_classes'] if package_info else 0
        duration_days = package_info['duration_days'] if package_info else 0
        
        # Calculate expiry date
        if class_plan == "No Package" or duration_days == 0:
            expiry_date = start_date
        else:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            expiry = start + timedelta(days=duration_days)
            expiry_date = expiry.strftime('%Y-%m-%d')
        
        query = '''
            INSERT INTO students (student_id, full_name, age, mobile, email, date_of_birth, 
                                sex, instrument, class_plan, total_classes, start_date, expiry_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        self.execute_update(query, (student_id, full_name, age, mobile, email, 
                                  date_of_birth, sex, instrument, class_plan, 
                                  total_classes, start_date, expiry_date))
        
        return student_id
    
    def get_all_students(self) -> List[tuple]:
        """Get all students with complete information"""
        query = '''
            SELECT id, student_id, full_name, age, mobile, instrument, class_plan,
                   total_classes, start_date, expiry_date, status, classes_completed,
                   extra_classes, first_class_date, email, date_of_birth, sex
            FROM students
            ORDER BY student_id
        '''
        return self.execute_query(query)
    
    def get_student_by_id(self, student_id: str) -> Optional[tuple]:
        """Get student by ID"""
        query = 'SELECT * FROM students WHERE student_id = ?'
        result = self.execute_query(query, (student_id,))
        return result[0] if result else None
    
    def update_student(self, student_id: str, **kwargs) -> bool:
        """Update student information"""
        if not kwargs:
            return False
        
        # Build dynamic update query
        set_clauses = []
        values = []
        
        for key, value in kwargs.items():
            set_clauses.append(f"{key} = ?")
            values.append(value)
        
        values.append(student_id)
        
        query = f"UPDATE students SET {', '.join(set_clauses)}, updated_at = CURRENT_TIMESTAMP WHERE student_id = ?"
        
        return self.execute_update(query, tuple(values)) > 0
    
    def delete_student(self, student_id: str) -> bool:
        """Delete student and all related records"""
        queries = [
            ('DELETE FROM attendance WHERE student_id = ?', (student_id,)),
            ('DELETE FROM payments WHERE student_id = ?', (student_id,)),
            ('DELETE FROM whatsapp_logs WHERE student_id = ?', (student_id,)),
            ('DELETE FROM email_logs WHERE student_id = ?', (student_id,)),
            ('DELETE FROM students WHERE student_id = ?', (student_id,))
        ]
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for query, params in queries:
                cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount > 0
    
    # Attendance Management
    def mark_attendance(self, student_id: str, attendance_type: str = 'Regular', 
                       notes: str = '') -> Tuple[bool, str]:
        """Mark student attendance"""
        student = self.get_student_by_id(student_id)
        
        if not student:
            return False, "Student not found"
        
        # Parse student data (adjust indices based on your table structure)
        expiry_date = datetime.strptime(student[12], '%Y-%m-%d')  # Adjust index
        classes_completed = student[14]  # Adjust index
        total_classes = student[7]  # Adjust index
        
        now = datetime.now()
        
        # Determine attendance type
        if now > expiry_date:
            attendance_type = 'Extra'
            message = "Extra class marked (expired package)"
        elif classes_completed >= total_classes:
            attendance_type = 'Extra'
            message = "Extra class marked (package completed)"
        else:
            attendance_type = 'Regular'
            message = "Regular attendance marked"
        
        # Insert attendance record
        query = '''
            INSERT INTO attendance (student_id, date, time, attendance_type, notes)
            VALUES (?, ?, ?, ?, ?)
        '''
        
        self.execute_update(query, (student_id, now.strftime('%Y-%m-%d'), 
                                  now.strftime('%H:%M:%S'), attendance_type, notes))
        
        # Update student record
        if attendance_type == 'Regular':
            self.execute_update(
                'UPDATE students SET classes_completed = classes_completed + 1, first_class_date = COALESCE(first_class_date, ?) WHERE student_id = ?',
                (now.strftime('%Y-%m-%d'), student_id)
            )
        else:
            self.execute_update(
                'UPDATE students SET extra_classes = extra_classes + 1 WHERE student_id = ?',
                (student_id,)
            )
        
        return True, message
    
    # Payment Management
    def add_payment(self, student_id: str, amount: float, payment_method: str,
                   notes: str = '', next_due_date: str = '') -> str:
        """Add payment record"""
        # Generate receipt number
        count = self.execute_query('SELECT COUNT(*) FROM payments')[0][0]
        receipt_number = f"CMA{count + 1:05d}"
        
        query = '''
            INSERT INTO payments (student_id, amount, payment_date, receipt_number,
                                payment_method, notes, next_due_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
        
        self.execute_update(query, (student_id, amount, datetime.now().strftime('%Y-%m-%d'),
                                  receipt_number, payment_method, notes, next_due_date))
        
        return receipt_number
    
    def get_student_payments(self, student_id: str) -> List[tuple]:
        """Get all payments for a student"""
        query = 'SELECT * FROM payments WHERE student_id = ? ORDER BY payment_date DESC'
        return self.execute_query(query, (student_id,))
    
    def get_total_paid(self, student_id: str) -> float:
        """Get total amount paid by student"""
        query = 'SELECT COALESCE(SUM(amount), 0) FROM payments WHERE student_id = ?'
        result = self.execute_query(query, (student_id,))
        return result[0][0] if result else 0.0
    
    # Package Management
    def get_package_info(self, package_name: str) -> Optional[Dict[str, Any]]:
        """Get package information"""
        query = 'SELECT * FROM packages WHERE package_name = ? AND is_active = 1'
        result = self.execute_query(query, (package_name,))
        
        if result:
            row = result[0]
            return {
                'id': row[0],
                'package_name': row[1],
                'total_classes': row[2],
                'duration_days': row[3],
                'price': row[4],
                'description': row[5]
            }
        return None
    
    def get_all_packages(self) -> List[Dict[str, Any]]:
        """Get all active packages"""
        query = 'SELECT * FROM packages WHERE is_active = 1 ORDER BY duration_days'
        results = self.execute_query(query)
        
        packages = []
        for row in results:
            packages.append({
                'id': row[0],
                'package_name': row[1],
                'total_classes': row[2],
                'duration_days': row[3],
                'price': row[4],
                'description': row[5]
            })
        
        return packages
    
    # Dashboard Statistics
    def get_dashboard_stats(self) -> Tuple[int, int, int, int]:
        """Get dashboard statistics"""
        total = self.execute_query('SELECT COUNT(*) FROM students')[0][0]
        
        active = self.execute_query(
            'SELECT COUNT(*) FROM students WHERE expiry_date >= date("now")'
        )[0][0]
        
        expired = self.execute_query(
            'SELECT COUNT(*) FROM students WHERE expiry_date < date("now")'
        )[0][0]
        
        today_attendance = self.execute_query(
            'SELECT COUNT(*) FROM attendance WHERE date = date("now")'
        )[0][0]
        
        return total, active, expired, today_attendance
    
    # Communication Logging
    def log_whatsapp_message(self, student_id: str, mobile: str, message_type: str,
                           template_id: str, status: str, response_data: str = '') -> None:
        """Log WhatsApp message"""
        query = '''
            INSERT INTO whatsapp_logs (student_id, mobile_number, message_type, 
                                     template_id, status, response_data)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        
        self.execute_update(query, (student_id, mobile, message_type, 
                                  template_id, status, response_data))
    
    def log_email_message(self, student_id: str, email: str, subject: str,
                         message_type: str, status: str, error_message: str = '') -> None:
        """Log email message"""
        query = '''
            INSERT INTO email_logs (student_id, email_address, subject, 
                                  message_type, status, error_message)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        
        self.execute_update(query, (student_id, email, subject, 
                                  message_type, status, error_message))
    
    # System Settings
    def get_setting(self, key: str) -> Optional[str]:
        """Get system setting value"""
        query = 'SELECT setting_value FROM system_settings WHERE setting_key = ?'
        result = self.execute_query(query, (key,))
        return result[0][0] if result else None
    
    def set_setting(self, key: str, value: str, description: str = '') -> None:
        """Set system setting value"""
        query = '''
            INSERT OR REPLACE INTO system_settings (setting_key, setting_value, description, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        '''
        
        self.execute_update(query, (key, value, description))
    
    # Utility Methods
    def backup_database(self, backup_path: str = None) -> str:
        """Create database backup"""
        if not backup_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f"chords_crm_backup_{timestamp}.db"
        
        import shutil
        shutil.copy2(self.db_path, backup_path)
        return backup_path
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get database information"""
        tables = self.execute_query("SELECT name FROM sqlite_master WHERE type='table'")
        
        info = {
            'database_path': os.path.abspath(self.db_path),
            'database_size': os.path.getsize(self.db_path),
            'tables': []
        }
        
        for table in tables:
            table_name = table[0]
            count = self.execute_query(f"SELECT COUNT(*) FROM {table_name}")[0][0]
            info['tables'].append({'name': table_name, 'records': count})
        
        return info

# Global database manager instance
db_manager = DatabaseManager()

# Legacy function compatibility
def init_db():
    """Initialize database (legacy compatibility)"""
    db_manager.ensure_database_exists()

def get_next_student_id():
    """Get next student ID (legacy compatibility)"""
    return db_manager.get_next_student_id()

def add_student(full_name, age, mobile, email, date_of_birth, sex, instrument, class_plan, start_date, expiry_date=None):
    """Add student (legacy compatibility)"""
    return db_manager.add_student(full_name, age, mobile, email, date_of_birth, sex, instrument, class_plan, start_date)

def mark_attendance(student_id):
    """Mark attendance (legacy compatibility)"""
    return db_manager.mark_attendance(student_id)

def get_all_students():
    """Get all students (legacy compatibility)"""
    return db_manager.get_all_students()

def get_dashboard_stats():
    """Get dashboard stats (legacy compatibility)"""
    return db_manager.get_dashboard_stats()