import sqlite3
from datetime import datetime, timedelta
import re

def init_db():
    conn = sqlite3.connect('chords_crm.db')
    cursor = conn.cursor()
    
    # Students table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
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
        )
    ''')
    
    # Add new columns if they don't exist
    try:
        cursor.execute('ALTER TABLE students ADD COLUMN email TEXT')
    except:
        pass
    try:
        cursor.execute('ALTER TABLE students ADD COLUMN date_of_birth TEXT')
    except:
        pass
    try:
        cursor.execute('ALTER TABLE students ADD COLUMN sex TEXT')
    except:
        pass
    
    # Add new columns if they don't exist
    try:
        cursor.execute('ALTER TABLE students ADD COLUMN extra_classes INTEGER DEFAULT 0')
    except:
        pass
    try:
        cursor.execute('ALTER TABLE students ADD COLUMN first_class_date TEXT')
    except:
        pass
    
    # Attendance table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            date TEXT,
            time TEXT,
            FOREIGN KEY (student_id) REFERENCES students (student_id)
        )
    ''')
    
    # Payments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            amount REAL,
            payment_date TEXT,
            receipt_number TEXT,
            FOREIGN KEY (student_id) REFERENCES students (student_id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_next_student_id():
    conn = sqlite3.connect('chords_crm.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM students')
    count = cursor.fetchone()[0]
    conn.close()
    return f"CHORDS{count + 1:03d}"

def add_student(full_name, age, mobile, email, date_of_birth, sex, instrument, class_plan, start_date, expiry_date=None):
    conn = sqlite3.connect('chords_crm.db')
    cursor = conn.cursor()
    
    student_id = get_next_student_id()
    
    # Calculate total classes and expiry date based on package duration
    class_plans = {"1 Month - 8": (8, 30), "3 Month - 24": (24, 90), "6 Month - 48": (48, 180), "12 Month - 96": (96, 365)}
    total_classes, package_days = class_plans[class_plan]
    
    if expiry_date:
        expiry = datetime.strptime(expiry_date, '%Y-%m-%d')
    else:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        expiry = start + timedelta(days=package_days)
    
    cursor.execute('''
        INSERT INTO students (student_id, full_name, age, mobile, email, date_of_birth, sex, instrument, class_plan, 
                            total_classes, start_date, expiry_date, first_class_date, extra_classes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (student_id, full_name, age, mobile, email, date_of_birth, sex, instrument, class_plan, 
          total_classes, start_date, expiry.strftime('%Y-%m-%d'), None, 0))
    
    conn.commit()
    conn.close()
    return student_id

def mark_attendance(student_id):
    conn = sqlite3.connect('chords_crm.db')
    cursor = conn.cursor()
    
    # Check if student exists and is active
    cursor.execute('SELECT * FROM students WHERE student_id = ?', (student_id,))
    student = cursor.fetchone()
    
    if not student:
        conn.close()
        return False, "Student not found"
    
    # Check if expired
    expiry_date = datetime.strptime(student[9], '%Y-%m-%d')
    if datetime.now() > expiry_date:
        # Allow extra classes after expiry (makeup classes)
        cursor.execute('''
            INSERT INTO attendance (student_id, date, time)
            VALUES (?, ?, ?)
        ''', (student_id, datetime.now().strftime('%Y-%m-%d'), datetime.now().strftime('%H:%M:%S')))
        
        cursor.execute('''
            UPDATE students SET extra_classes = extra_classes + 1
            WHERE student_id = ?
        ''', (student_id,))
        
        conn.commit()
        conn.close()
        return True, "Extra class marked (can be used as makeup)"
    
    # Set first class date if not set
    if not student[13]:  # first_class_date is None
        cursor.execute('''
            UPDATE students SET first_class_date = ?
            WHERE student_id = ?
        ''', (datetime.now().strftime('%Y-%m-%d'), student_id))
    
    # Extract numbers using regex
    def extract_number(value):
        match = re.search(r'\d+', str(value))
        return int(match.group()) if match else 0
    
    # Check if regular classes completed
    if int(student[11]) >= extract_number(student[6]):  # classes_completed >= total_classes
        # Mark as extra class
        cursor.execute('''
            INSERT INTO attendance (student_id, date, time)
            VALUES (?, ?, ?)
        ''', (student_id, datetime.now().strftime('%Y-%m-%d'), datetime.now().strftime('%H:%M:%S')))
        
        cursor.execute('''
            UPDATE students SET extra_classes = extra_classes + 1
            WHERE student_id = ?
        ''', (student_id,))
        
        conn.commit()
        conn.close()
        return True, "Extra class marked (can be used as makeup)"
    
    # Mark regular attendance
    now = datetime.now()
    cursor.execute('''
        INSERT INTO attendance (student_id, date, time)
        VALUES (?, ?, ?)
    ''', (student_id, now.strftime('%Y-%m-%d'), now.strftime('%H:%M:%S')))
    
    # Update classes completed
    cursor.execute('''
        UPDATE students SET classes_completed = classes_completed + 1
        WHERE student_id = ?
    ''', (student_id,))
    
    conn.commit()
    conn.close()
    return True, "Attendance marked successfully"

def get_all_students():
    conn = sqlite3.connect('chords_crm.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM students')
    students = cursor.fetchall()
    conn.close()
    return students

def get_dashboard_stats():
    conn = sqlite3.connect('chords_crm.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM students')
    total_students = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM students WHERE expiry_date >= date("now")')
    active_students = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM students WHERE expiry_date < date("now")')
    expired_students = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM attendance WHERE date = date("now")')
    today_attendance = cursor.fetchone()[0]
    
    conn.close()
    return total_students, active_students, expired_students, today_attendance