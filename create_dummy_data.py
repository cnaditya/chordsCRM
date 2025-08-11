from database import init_db, add_student
from datetime import datetime, timedelta
import sqlite3

def create_dummy_students():
    init_db()  # Initialize database first
    
    conn = sqlite3.connect('chords_crm.db')
    cursor = conn.cursor()
    
    # Check if students already exist
    cursor.execute('SELECT COUNT(*) FROM students')
    if cursor.fetchone()[0] > 0:
        print("Dummy data already exists!")
        conn.close()
        return
    
    # Dummy student data with manual student IDs
    students = [
        ("CHORDS001", "Arjun Sharma", 25, "9876543210", "Guitar", "Monthly - 8", 8, "2024-12-01", "2025-01-01", 6),
        ("CHORDS002", "Priya Patel", 22, "9876543211", "Piano", "Quarterly - 24", 24, "2024-11-15", "2025-02-15", 18),
        ("CHORDS003", "Rahul Kumar", 28, "9876543212", "Drums", "Half-Yearly - 48", 48, "2024-10-01", "2025-04-01", 35),
        ("CHORDS004", "Sneha Reddy", 24, "9876543213", "Violin", "Yearly - 96", 96, "2024-09-01", "2025-09-01", 80),
        ("CHORDS005", "Vikram Singh", 26, "9876543214", "Carnatic Vocals", "Monthly - 8", 8, "2024-11-15", "2024-12-15", 9)
    ]
    
    for student_id, name, age, mobile, instrument, plan, total_classes, start_date, expiry_date, completed in students:
        cursor.execute('''
            INSERT INTO students (student_id, full_name, age, mobile, instrument, class_plan, 
                                total_classes, start_date, expiry_date, classes_completed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (student_id, name, age, mobile, instrument, plan, total_classes, start_date, expiry_date, completed))
        print(f"Created: {student_id} - {name} ({completed}/{total_classes} classes)")
    
    conn.commit()
    conn.close()
    print("\n✅ Dummy data created successfully!")
    print("- CHORDS005 (Vikram) is OVERDUE (expired 2024-12-15)")
    print("- CHORDS001 (Arjun) has 2 classes remaining")
    print("- CHORDS004 (Sneha) has 16 classes remaining")

if __name__ == "__main__":
    create_dummy_students()