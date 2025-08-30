#!/usr/bin/env python3
"""
Clean database and load only the 33 students provided
"""

import sqlite3
from datetime import datetime, timedelta
import re

def parse_date(date_str):
    """Parse various date formats to YYYY-MM-DD"""
    if not date_str or date_str.strip() == "":
        return None
    
    date_str = str(date_str).strip()
    
    formats = [
        '%d-%B-%Y',      # 31-July-2007
        '%d%B%Y',        # 26July2013
        '%d%b%Y',        # 2May2013
        '%B%d %Y',       # March12 2020
        '%Y-%b-%d',      # 2012-Aug-23
        '%b%d-%Y',       # nov25-2012
        '%b%d , %Y',     # june24 , 2016
        '%d%b%Y',        # 18Apr2019
        '%d%b%Y',        # 02Mar2017
        '%d%b%Y',        # 07Apr2013
        '%d-%b-%Y',      # 14-Sep2025
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
        except:
            continue
    
    return None

def parse_expiry_date(expiry_str):
    """Parse expiry date formats"""
    if not expiry_str or expiry_str.strip() == "":
        return None
    
    expiry_str = str(expiry_str).strip()
    
    formats = [
        '%d-%b-%Y',      # 01-Sep-2025
        '%d-%B-%Y',      # 01-September-2025
        '%d%b%Y',        # 14Sep2025
        '%d-%b-%Y',      # 13-July-2026
        '%d-Jan-%Y',     # 6-Jan-2025
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(expiry_str, fmt).strftime('%Y-%m-%d')
        except:
            continue
    
    return None

def map_package(package_str):
    """Map package description to standard format"""
    if not package_str:
        return "No Package"
    
    package_str = str(package_str).lower().strip()
    
    if "1 month" in package_str or "1month" in package_str:
        return "1 Month - 8"
    elif "3 month" in package_str or "3months" in package_str:
        return "3 Month - 24"
    elif "6 month" in package_str or "6months" in package_str:
        return "6 Month - 48"
    elif "1 year" in package_str or "12 month" in package_str:
        return "12 Month - 96"
    elif "8 classes" in package_str:
        return "1 Month - 8"
    else:
        return "No Package"

def calculate_age(dob_str):
    """Calculate age from date of birth"""
    if not dob_str:
        return None
    
    try:
        dob = datetime.strptime(dob_str, '%Y-%m-%d')
        today = datetime.now()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return age
    except:
        return None

def clean_and_load_students():
    """Clear database and load only the 33 students"""
    
    # Student data - exactly as provided
    students_data = [
        ("Guru", "9849820758", "gurusri.nallamolu@gmail.com", "31-July-2007", "Guitar", "8500", "3months", "01-Sep-2025"),
        ("Sohan", "9849820758", "gurusri.nallamolu@gmail.com", "26July2013", "Keyboard", "8500", "3months", "01-Sep-2025"),
        ("Jyotsna", "9966692628", "rajyalakshmi.rl@gmail.com", "2May2013", "Guitar", "3000", "8 classes", "01-Sep-2025"),
        ("Riya", "9100323223", "durgaprasad.boni@gmail.com", "March12 2020", "carnatic vocal", "", "3 Months", "01-Sep-2025"),
        ("Tanay", "9848147296", "rohini11chowdary@gmail.com", "2012-Aug-23", "Guitar", "", "8 classes", "01-Sep-2025"),
        ("Veesam Preetham Reddy", "9550249884", "", "nov25-2012", "Guitar", "3000", "8 classes", "01-Oct-2025"),
        ("Veesam Shriyan Reddy", "9550249884", "", "june24 , 2016", "Drums", "3000", "8 classes", "01-Oct-2025"),
        ("Shankar M", "9133268187", "", "", "Keyboard", "3000", "8 classes", "01-Sep-2025"),
        ("Sashmitha", "9582764399", "", "", "Carnatic vocal", "", "3 Months", "07-Sep-2025"),
        ("Prekshana", "9912285312", "", "", "Keyboard", "8500", "3 Months", "07-Sep-2025"),
        ("M Sreephani", "9347475589", "", "", "Guitar", "36000", "1 year", "14-Jun-2026"),
        ("G Aarshika Reddy", "9966979620", "", "", "Carnatic vocal", "32000", "1 year", "13-Jun-2026"),
        ("G Gautham", "9000527642", "", "", "Drums", "", "3 Months", "16-Sep-2025"),
        ("Aditya Palagummi", "9701802225", "", "", "Guitar", "", "3 Months", "22-September-2025"),
        ("Pranav Keerthana", "9701802225", "", "", "Keyboard", "", "3 Months", "22-September-2025"),
        ("Aranya AshokKumar", "9987503447", "", "", "Drums", "20000", "6Months", ""),
        ("Iniya", "9987503447", "mail2ashokkumar@gmail.com", "18Apr2019", "Keyboard", "20000", "6Months", ""),
        ("Praveen B", "8074549233", "", "", "Drums", "10000", "3months", "23-Sep-2025"),
        ("Manikanta", "9010906083", "", "", "Keyboard", "10000", "3months", "1-Oct-2025"),
        ("Shreyas", "9908892088", "", "", "Guitar", "9500", "3months", "5-Oct-2025"),
        ("Saanvi", "9908892088", "", "", "Keyboard", "9500", "3months", "5-Oct-2025"),
        ("Viyaan K", "7989865793", "", "", "Keyboard", "10000", "3Months", "12-Oct-2025"),
        ("Ashutosh Garnayk", "9861152500", "", "", "Keyboard", "20400", "6months", "6-Jan-2025"),
        ("Virupaksha", "7022114252", "", "", "Keyboard", "10000", "3months", "12-Oct-2025"),
        ("Kushal", "9885829803", "", "", "Drums", "10000", "1 year", "13-July-2026"),
        ("Riyansh", "9849945556", "", "", "Keyboard", "9600", "3months", "01-Nov-2025"),
        ("sowdham", "7993837248", "", "", "Keyboard", "10000", "3months", "01-Nov-2025"),
        ("dedeepya", "9743035347", "", "", "Guitar", "10000", "3 months", "01-Nov-2025"),
        ("vishnu", "7032223535", "", "", "Guitar", "8000", "1month", "10-Sep-2025"),
        ("Chetana", "8121006676", "", "02Mar2017", "Keyboard", "3000", "1month", "01-Sep-2025"),
        ("J Rajinikanth", "9059883572", "", "", "Keyboard", "4000", "1month", "10-Sep-2025"),
        ("Havish N", "8801003055", "", "", "Drums", "4500", "1month", "01-Sep-2025"),
        ("Anvi", "7032653281", "", "07Apr2013", "Keyboard", "4000", "1month", "14-Sep2025"),
    ]
    
    conn = sqlite3.connect('chords_crm.db')
    cursor = conn.cursor()
    
    # Clear all existing data
    cursor.execute('DELETE FROM attendance')
    cursor.execute('DELETE FROM payments')
    cursor.execute('DELETE FROM students')
    
    print("🗑️ Cleared existing data")
    
    success_count = 0
    
    for i, (name, mobile, email, dob, instrument, fees, package, expiry) in enumerate(students_data, 1):
        try:
            student_id = f"CHORDS{i:03d}"
            
            # Parse dates
            parsed_dob = parse_date(dob)
            parsed_expiry = parse_expiry_date(expiry)
            
            # Calculate age
            age = calculate_age(parsed_dob) if parsed_dob else None
            
            # Map package
            class_plan = map_package(package)
            
            # Calculate total classes
            class_plans = {
                "No Package": 0,
                "1 Month - 8": 8,
                "3 Month - 24": 24,
                "6 Month - 48": 48,
                "12 Month - 96": 96
            }
            total_classes = class_plans.get(class_plan, 0)
            
            # Use expiry date or calculate start date
            if parsed_expiry:
                expiry_date = parsed_expiry
                # Calculate approximate start date
                if "3 Month" in class_plan:
                    start_date = (datetime.strptime(expiry_date, '%Y-%m-%d') - timedelta(days=90)).strftime('%Y-%m-%d')
                elif "6 Month" in class_plan:
                    start_date = (datetime.strptime(expiry_date, '%Y-%m-%d') - timedelta(days=180)).strftime('%Y-%m-%d')
                elif "12 Month" in class_plan:
                    start_date = (datetime.strptime(expiry_date, '%Y-%m-%d') - timedelta(days=365)).strftime('%Y-%m-%d')
                else:
                    start_date = (datetime.strptime(expiry_date, '%Y-%m-%d') - timedelta(days=30)).strftime('%Y-%m-%d')
            else:
                # Default start date to today
                start_date = datetime.now().strftime('%Y-%m-%d')
                expiry_date = start_date
            
            # Insert student
            cursor.execute('''
                INSERT INTO students (student_id, full_name, age, mobile, email, date_of_birth, sex, instrument, 
                                    class_plan, total_classes, start_date, expiry_date, classes_completed, extra_classes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (student_id, name, age, mobile, email or None, parsed_dob, None, instrument, 
                  class_plan, total_classes, start_date, expiry_date, 0, 0))
            
            success_count += 1
            print(f"✓ Added: {name} ({student_id})")
            
        except Exception as e:
            print(f"✗ Error adding {name}: {str(e)}")
    
    conn.commit()
    conn.close()
    
    print(f"\n📊 Summary:")
    print(f"✓ Successfully added: {success_count} students")
    print(f"🎯 Total students in database: {success_count}")

if __name__ == "__main__":
    clean_and_load_students()