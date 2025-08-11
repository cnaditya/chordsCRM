import sqlite3

def update_dummy_data():
    conn = sqlite3.connect('chords_crm.db')
    cursor = conn.cursor()
    
    # Clear existing data
    cursor.execute('DELETE FROM students')
    cursor.execute('DELETE FROM attendance')
    
    # Insert new dummy data with package format
    students = [
        ("CHORDS001", "Arjun Sharma", 25, "9876543210", "Guitar", "1 Month - 8", 8, "2024-12-01", "2024-12-31", 6, 2, "2024-12-03"),
        ("CHORDS002", "Priya Patel", 22, "9876543211", "Piano", "3 Month - 24", 24, "2024-11-15", "2025-02-15", 18, 0, "2024-11-17"),
        ("CHORDS003", "Rahul Kumar", 28, "9876543212", "Drums", "6 Month - 48", 48, "2024-10-01", "2025-04-01", 35, 3, "2024-10-03"),
        ("CHORDS004", "Sneha Reddy", 24, "9876543213", "Violin", "12 Month - 96", 96, "2024-09-01", "2025-09-01", 80, 1, "2024-09-05"),
        ("CHORDS005", "Vikram Singh", 26, "9876543214", "Carnatic Vocals", "1 Month - 8", 8, "2024-11-15", "2024-12-15", 9, 4, "2024-11-18")
    ]
    
    for student_id, name, age, mobile, instrument, plan, total_classes, start_date, expiry_date, completed, extra, first_class in students:
        cursor.execute('''
            INSERT INTO students (student_id, full_name, age, mobile, instrument, class_plan, 
                                total_classes, start_date, expiry_date, classes_completed, extra_classes, first_class_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (student_id, name, age, mobile, instrument, plan, total_classes, start_date, expiry_date, completed, extra, first_class))
        print(f"Updated: {student_id} - {name} ({completed}/{total_classes} + {extra} extra)")
    
    conn.commit()
    conn.close()
    print("\n✅ Dummy data updated with package format and extra classes!")

if __name__ == "__main__":
    update_dummy_data()