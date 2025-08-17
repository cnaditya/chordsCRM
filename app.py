import streamlit as st
import pandas as pd
from datetime import datetime, date
import sqlite3
from database import init_db, add_student, mark_attendance, get_all_students, get_dashboard_stats
from mantra_simple import mantra_scanner as scanner
from sms_email import send_whatsapp_reminder, send_payment_receipt_email
from style import apply_custom_css, get_instrument_emoji, display_header, display_metric_card
# Security module removed
import os

# Initialize database and styling
init_db()

# Initialize scanner connection on startup
try:
    scanner.connect_scanner()
except:
    pass
st.set_page_config(page_title="Chords Music Academy CRM", page_icon="🎵", layout="wide")
apply_custom_css()

# IP Management Functions
def load_allowed_ips():
    """Load allowed IPs from database"""
    try:
        conn = sqlite3.connect('chords_crm.db')
        cursor = conn.cursor()
        
        # Create IP table if not exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS allowed_ips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip_address TEXT UNIQUE,
                description TEXT,
                added_date TEXT
            )
        ''')
        
        # Add default IPs if table is empty
        cursor.execute('SELECT COUNT(*) FROM allowed_ips')
        if cursor.fetchone()[0] == 0:
            default_ips = [
                ('192.168.0.', 'Local network range'),
                ('49.204.30.164', 'Office IP'),
                ('49.204.28.147', 'Home IP'),
                ('35.197.92.111', 'Streamlit Cloud Server'),
                ('127.0.0.1', 'Localhost')
            ]
            for ip, desc in default_ips:
                cursor.execute('INSERT INTO allowed_ips (ip_address, description, added_date) VALUES (?, ?, ?)',
                             (ip, desc, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        
        # Always ensure Streamlit Cloud IP is present
        cursor.execute('INSERT OR IGNORE INTO allowed_ips (ip_address, description, added_date) VALUES (?, ?, ?)',
                      ('35.197.92.111', 'Streamlit Cloud Server', datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        
        cursor.execute('SELECT ip_address FROM allowed_ips')
        ips = [row[0] for row in cursor.fetchall()]
        conn.commit()
        conn.close()
        return ips
    except:
        # Fallback to hardcoded IPs including Streamlit Cloud
        return ["192.168.0.", "49.204.30.164", "49.204.28.147", "35.197.92.111", "127.0.0.1"]

def add_allowed_ip(ip_address, description):
    """Add new allowed IP"""
    try:
        conn = sqlite3.connect('chords_crm.db')
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO allowed_ips (ip_address, description, added_date) VALUES (?, ?, ?)',
                      (ip_address, description, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def remove_allowed_ip(ip_address):
    """Remove allowed IP"""
    try:
        conn = sqlite3.connect('chords_crm.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM allowed_ips WHERE ip_address = ?', (ip_address,))
        conn.commit()
        conn.close()
        return True
    except:
        return False

# Load allowed IPs dynamically
ALLOWED_IPS = load_allowed_ips()

def check_secure_access():
    """Multi-layer security check"""
    from datetime import datetime, time
    import hashlib
    
    # 1. Business Hours Check (9 AM to 8 PM)
    current_time = datetime.now().time()
    business_start = time(9, 0)  # 9:00 AM
    business_end = time(20, 0)   # 8:00 PM
    
    if not (business_start <= current_time <= business_end):
        return False
    
    # 2. Weekday Check (Monday to Saturday)
    current_day = datetime.now().weekday()  # 0=Monday, 6=Sunday
    if current_day == 6:  # Sunday
        return False
    
    # 3. Device Fingerprinting (Browser-based)
    try:
        import streamlit.components.v1 as components
        
        # Get browser fingerprint
        fingerprint_script = """
        <script>
        const fingerprint = navigator.userAgent + screen.width + screen.height + navigator.language;
        const hash = btoa(fingerprint).substring(0, 16);
        window.parent.postMessage({type: 'device_fingerprint', fingerprint: hash}, '*');
        </script>
        """
        
        components.html(fingerprint_script, height=0)
        
        # Check if device is authorized (stored in session)
        if 'authorized_device' not in st.session_state:
            # First time access - require admin approval
            if 'pending_device' not in st.session_state:
                st.session_state.pending_device = True
                return False
        
    except:
        pass
    
    # 4. Session timeout (4 hours)
    if 'session_start' in st.session_state:
        session_duration = datetime.now() - st.session_state.session_start
        if session_duration.total_seconds() > 14400:  # 4 hours
            del st.session_state.session_start
            return False
    
    return True

def get_user_ip():
    """Get user's real IP address"""
    try:
        # Try JavaScript-based IP detection first
        import streamlit.components.v1 as components
        
        # Use ipify service for reliable IP detection
        ip_script = """
        <script>
        fetch('https://api.ipify.org?format=json')
        .then(response => response.json())
        .then(data => {
            window.parent.postMessage({type: 'user_ip', ip: data.ip}, '*');
        })
        .catch(() => {
            window.parent.postMessage({type: 'user_ip', ip: '127.0.0.1'}, '*');
        });
        </script>
        """
        
        # Execute JavaScript to get IP
        components.html(ip_script, height=0)
        
        # Fallback to session state if available
        if 'detected_ip' in st.session_state:
            return st.session_state.detected_ip
        
        # Final fallback - try requests
        import requests
        response = requests.get('https://api.ipify.org', timeout=3)
        return response.text.strip()
        
    except:
        return '127.0.0.1'

def check_ip_access():
    """Check if user's IP is allowed"""
    try:
        # Get user's IP
        user_ip = get_user_ip()
        
        # Store for display
        st.session_state.current_user_ip = user_ip
        
        # Get allowed IPs from database
        current_ips = load_allowed_ips()
        
        # Check if IP is in allowed range
        for allowed_ip in current_ips:
            if user_ip.startswith(allowed_ip):
                return True
        
        # Debug: Show IP in error for testing
        st.session_state.debug_ip = user_ip
        return False
        
    except Exception as e:
        # Store error for debugging
        st.session_state.ip_error = str(e)
        return False

# Login function
def login():
    display_header("Chords Music Academy")
    
    # No access restrictions - normal login only
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 🔐 Admin Login - Secure Access")
        
        # Login form with Enter key support
        with st.form("login_form"):
            username = st.text_input("👤 Username")
            password = st.text_input("🔒 Password", type="password")
            login_button = st.form_submit_button("🚀 Login", use_container_width=True)
            
            if login_button:
                if username == "admin" and password == "admin1":
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials")

# Main dashboard
def dashboard():
    display_header("Executive Dashboard", "Comprehensive Student Management System")
    
    # Get stats
    total, active, expired, today_att = get_dashboard_stats()
    
    # Key Metrics Section
    st.markdown('<div class="metrics-grid">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        display_metric_card("Total Students", total, "👥", "#3b82f6")
    with col2:
        display_metric_card("Active Students", active, "✅", "#10b981")
    with col3:
        display_metric_card("Expired Plans", expired, "⚠️", "#f59e0b")
    with col4:
        display_metric_card("Today's Attendance", today_att, "📅", "#8b5cf6")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Management Console
    display_section_header("Management Console")
    
    # Navigation Grid
    st.markdown('<div class="dashboard-grid">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="nav-card">
            <div class="nav-card-icon">👥</div>
            <div class="nav-card-title">Student Management</div>
            <div class="nav-card-desc">Register new students and manage existing records</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📝 Student Registration", use_container_width=True):
            st.session_state.page = "registration"
            st.rerun()
        if st.button("👥 Student List & Edit", use_container_width=True):
            st.session_state.page = "student_list"
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="nav-card">
            <div class="nav-card-icon">📈</div>
            <div class="nav-card-title">Operations</div>
            <div class="nav-card-desc">Attendance tracking and biometric enrollment</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("✅ Attendance Management", use_container_width=True):
            st.session_state.page = "attendance"
            st.rerun()
        if st.button("🔒 Biometric Enrollment", use_container_width=True):
            st.session_state.page = "biometric"
            st.rerun()
    
    with col3:
        st.markdown("""
        <div class="nav-card">
            <div class="nav-card-icon">💰</div>
            <div class="nav-card-title">Financial</div>
            <div class="nav-card-desc">Payment processing and financial reports</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("💰 Payment Processing", use_container_width=True):
            st.session_state.page = "payments"
            st.rerun()
        if st.button("📊 Analytics & Reports", use_container_width=True):
            st.session_state.page = "reports"
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Alerts Section
    if expired > 0:
        st.markdown("""
        <div class="alert-warning">
            <strong>⚠️ Attention Required:</strong> {expired} students have expired payment plans that need immediate attention.
        </div>
        """.format(expired=expired), unsafe_allow_html=True)
        
        if st.button("🚨 View Due Alerts & Take Action", use_container_width=True, type="primary"):
            st.session_state.page = "due_alerts"
            st.rerun()

# Student registration
def student_registration():
    display_header("Student Registration")
    
    # Form inputs outside to enable real-time updates
    full_name = st.text_input("Full Name")
    age = st.number_input("Age", min_value=1, max_value=100)
    mobile = st.text_input("Mobile Number")
    email = st.text_input("Email Address")
    from datetime import date
    date_of_birth = st.date_input("Date of Birth", 
                                 min_value=date(1950, 1, 1),
                                 max_value=date.today(),
                                 value=date(2010, 1, 1))
    sex = st.selectbox("Gender", ["Male", "Female", "Other"])
    
    instruments = [
        "Keyboard", "Piano", "Guitar", "Drums", "Violin", 
        "Flute", "Carnatic Vocals", "Hindustani Vocals", "Western Vocals"
    ]
    instrument_options = [f"{get_instrument_emoji(inst)} {inst}" for inst in instruments]
    selected = st.selectbox("🎼 Instrument", instrument_options)
    instrument = selected.split(" ", 1)[1]
    
    start_date = st.date_input("Start Date", value=date.today())
    
    # Submit button
    if st.button("Register Student", type="primary"):

            if full_name and mobile and email:
                student_id = add_student(full_name, age, mobile, email, 
                                       date_of_birth.strftime('%Y-%m-%d'), sex, instrument,
                                       "1 Month - 8", start_date.strftime('%Y-%m-%d'))  # Default plan
                
                st.markdown(f"""
                <div class="success-msg">
                    <h3>🎉 Registration Successful!</h3>
                    <p><strong>Student ID:</strong> {student_id}</p>
                    <p>📱 Next: Proceed to Biometric Enrollment</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("Please fill all required fields (Name, Mobile, Email)")
    
    if st.button("← Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()

# Biometric enrollment module
def biometric_enrollment():
    display_header("Biometric Enrollment")
    
    # Scanner connection status
    col1, col2 = st.columns(2)
    with col1:
        if scanner.is_connected:
            st.success("🟢 Scanner Connected")
        else:
            st.error("🔴 Scanner Disconnected")
    
    with col2:
        if st.button("🔌 Connect Scanner", use_container_width=True):
            success, message = scanner.connect_scanner()
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
        
        st.info(f"📊 Enrolled: {scanner.get_enrolled_count()} students")
    
    st.divider()
    
    # Search and filter section
    enrollment_type = st.radio(
        "Select Enrollment Method:",
        ["Search Student", "Show All Students", "Not Enrolled Only"],
        horizontal=True
    )
    
    students = get_all_students()
    if students:
        df = pd.DataFrame(students, columns=[
            'ID', 'Student ID', 'Full Name', 'Age', 'Mobile', 'Instrument', 'Class Plan', 
            'Total Classes', 'Start Date', 'Expiry Date', 'Status', 'Classes Completed', 
            'Extra Classes', 'First Class Date', 'Email', 'Date of Birth', 'Sex'
        ])
        
        if enrollment_type == "Search Student":
            search_term = st.text_input("🔍 Enter Student Name or ID for Enrollment:", placeholder="Type student name or ID")
            
            if search_term:
                df = df[df['Full Name'].str.contains(search_term, case=False, na=False) | 
                       df['Student ID'].str.contains(search_term, case=False, na=False)]
                
                if df.empty:
                    st.warning("🔍 No student found with that name or ID.")
                else:
                    st.success(f"🎯 Found {len(df)} student(s) matching your search.")
            else:
                st.info("🔍 Please enter a student name or ID to search.")
                df = df.iloc[0:0]  # Empty dataframe
        
        elif enrollment_type == "Not Enrolled Only":
            # Filter only students not enrolled
            not_enrolled = []
            for _, student in df.iterrows():
                if student['Student ID'] not in scanner.enrolled_fingerprints:
                    not_enrolled.append(student)
            
            if not_enrolled:
                df = pd.DataFrame(not_enrolled)
                st.warning(f"⚠️ {len(df)} students need biometric enrollment.")
            else:
                st.success("🎉 All students are enrolled!")
                df = df.iloc[0:0]  # Empty dataframe
        
        else:  # Show All Students
            st.info(f"📋 Showing all {len(df)} students.")
        
        # Display students for enrollment
        if not df.empty:
            st.markdown("### 👆 Biometric Enrollment")
            
            for _, student in df.iterrows():
                emoji = get_instrument_emoji(student['Instrument'])
                enrolled = student['Student ID'] in scanner.enrolled_fingerprints
                status_icon = "✅" if enrolled else "❌"
                
                with st.expander(f"{status_icon} {emoji} {student['Full Name']} - {student['Student ID']} ({'Enrolled' if enrolled else 'Not Enrolled'})"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Student ID", student['Student ID'])
                        st.metric("Instrument", student['Instrument'])
                    
                    with col2:
                        st.metric("Mobile", student['Mobile'])
                        st.metric("Class Plan", student['Class Plan'])
                    
                    with col3:
                        if enrolled:
                            st.success("✅ Fingerprint Enrolled")
                        else:
                            st.warning("❌ Not Enrolled")
                            
                            if scanner.is_connected:
                                if st.button(f"👆 Enroll Fingerprint", key=f"enroll_{student['Student ID']}", use_container_width=True, type="primary"):
                                    with st.spinner("📱 Enrolling fingerprint..."):
                                        success, message = scanner.enroll_fingerprint(student['Student ID'])
                                        if success:
                                            st.success(message)
                                            st.rerun()
                                        else:
                                            st.error(message)
                            else:
                                st.error("🔴 Scanner not connected")
    else:
        st.info("No students registered yet.")
    
    if st.button("← Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()

# Attendance marking
def attendance_module():
    display_header("Attendance Marking")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Manual Entry")
        student_id = st.text_input("Enter Student ID")
        
        if st.button("Mark Attendance"):
            if student_id:
                success, message = mark_attendance(student_id)
                if success:
                    st.success(message)
                else:
                    st.error(message)
            else:
                st.error("Please enter Student ID")
    
    with col2:
        st.subheader("🔒 Biometric Attendance")
        
        # Scanner status
        if scanner.is_connected:
            st.success("🟢 Scanner Connected")
        else:
            st.error("🔴 Scanner Disconnected")
        
        col2a, col2b = st.columns(2)
        with col2a:
            if st.button("Connect Scanner"):
                success, message = scanner.connect_scanner()
                if success:
                    st.success(message)
                    st.rerun()
        
        with col2b:
            if st.button("Scan Fingerprint"):
                if scanner.is_connected:
                    with st.spinner("Scanning fingerprint..."):
                        success, student_id, message = scanner.scan_fingerprint()
                        if success:
                            att_success, att_message = mark_attendance(student_id)
                            if att_success:
                                st.success(f"Attendance marked for {student_id}")
                            else:
                                st.error(att_message)
                        else:
                            st.error(message)
                else:
                    st.error("Please connect scanner first")
                    
        st.markdown("---")
        st.info(f"🔧 Device: {scanner.get_device_info()}")
        st.info(f"📊 Total Enrolled: {scanner.get_enrolled_count()} students")
        
        st.info(f"📊 Enrolled fingerprints: {scanner.get_enrolled_count()}")
        st.info(f"🔧 {scanner.get_device_info()}")
    
    if st.button("← Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()

# Reports and dashboard
def reports_module():
    display_header("Attendance Summary Dashboard")
    
    students = get_all_students()
    if students:
        df = pd.DataFrame(students, columns=[
            'ID', 'Student ID', 'Full Name', 'Age', 'Mobile', 'Instrument',
            'Class Plan', 'Total Classes', 'Start Date', 'Expiry Date', 
            'Status', 'Classes Completed', 'Extra Classes', 'First Class Date'
        ])
        
        # Clean expiry dates and calculate status
        df['Expiry Date'] = df['Expiry Date'].astype(str).str.split(' ').str[0]
        df['Remaining Classes'] = df['Total Classes'] - df['Classes Completed']
        df['Status'] = df.apply(lambda row: 
            'Expired' if datetime.strptime(row['Expiry Date'], '%Y-%m-%d') < datetime.now()
            else 'Completed' if row['Classes Completed'] >= row['Total Classes']
            else 'Active', axis=1)
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            instrument_filter = st.selectbox("Filter by Instrument", 
                                           ['All'] + list(df['Instrument'].unique()))
        with col2:
            plan_filter = st.selectbox("Filter by Class Plan", 
                                     ['All'] + list(df['Class Plan'].unique()))
        
        # Apply filters
        filtered_df = df.copy()
        if instrument_filter != 'All':
            filtered_df = filtered_df[filtered_df['Instrument'] == instrument_filter]
        if plan_filter != 'All':
            filtered_df = filtered_df[filtered_df['Class Plan'] == plan_filter]
        
        # Clean start dates and calculate days enrolled
        filtered_df['Start Date'] = filtered_df['Start Date'].astype(str).str.split(' ').str[0]
        filtered_df['Days Enrolled'] = filtered_df.apply(lambda row: 
            (datetime.now() - datetime.strptime(row['Start Date'], '%Y-%m-%d')).days, axis=1)
        
        # Convert expiry date to datetime for editing
        filtered_df['Expiry Date'] = pd.to_datetime(filtered_df['Expiry Date'])
        
        # Display table with editable due dates
        display_df = filtered_df[['Student ID', 'Full Name', 'Instrument', 
                                'Classes Completed', 'Remaining Classes', 'Extra Classes', 'Days Enrolled', 'Expiry Date', 'Status']]
        
        # Make expiry date editable
        edited_df = st.data_editor(
            display_df,
            column_config={
                "Expiry Date": st.column_config.DateColumn(
                    "Due Date",
                    help="Click to edit due date",
                    format="DD-MM-YYYY"
                )
            },
            disabled=["Student ID", "Full Name", "Instrument", "Classes Completed", "Remaining Classes", "Extra Classes", "Days Enrolled", "Status"],
            hide_index=True
        )
        
        # Update database if dates changed
        if not edited_df.equals(display_df):
            conn = sqlite3.connect('chords_crm.db')
            cursor = conn.cursor()
            for idx, row in edited_df.iterrows():
                if row['Expiry Date'] != display_df.iloc[idx]['Expiry Date']:
                    cursor.execute("UPDATE students SET expiry_date = ? WHERE student_id = ?", 
                                 (row['Expiry Date'].strftime('%Y-%m-%d'), row['Student ID']))  # Keep internal format
            conn.commit()
            conn.close()
            st.success("Due dates updated successfully!")
            st.rerun()
        
        # Export to Excel
        if st.button("📥 Export to Excel"):
            excel_file = "student_report.xlsx"
            display_df.to_excel(excel_file, index=False)
            
            with open(excel_file, "rb") as file:
                st.download_button(
                    label="Download Excel Report",
                    data=file.read(),
                    file_name=excel_file,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    else:
        st.info("No students registered yet.")
    
    if st.button("← Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()

# Payment management
def payment_module():
    display_header("Fee Management")
    
    # Payment method selection
    payment_type = st.radio(
        "Select Payment Processing Method:",
        ["Search Student", "Due/Overdue Students Only"],
        horizontal=True
    )
    
    students = get_all_students()
    if students:
        # Database has 17 columns - use correct format
        df = pd.DataFrame(students, columns=[
            'ID', 'Student ID', 'Full Name', 'Age', 'Mobile', 'Instrument', 'Class Plan', 
            'Total Classes', 'Start Date', 'Expiry Date', 'Status', 'Classes Completed', 
            'Extra Classes', 'First Class Date', 'Email', 'Date of Birth', 'Sex'
        ])
        
        # Clean dates and calculate status
        df['Expiry Date'] = df['Expiry Date'].astype(str).str.split(' ').str[0]
        
        def get_status(row):
            try:
                if row['Expiry Date'] and '-' in str(row['Expiry Date']):
                    return 'Expired' if datetime.strptime(row['Expiry Date'], '%Y-%m-%d') < datetime.now() else 'Active'
                else:
                    return 'Active'
            except:
                return 'Active'
        
        df['Status'] = df.apply(get_status, axis=1)
        
        if payment_type == "Search Student":
            # Search specific student
            search_term = st.text_input("🔍 Enter Student Name or ID to Process Payment:", placeholder="Type student name or ID")
            
            if search_term:
                df = df[df['Full Name'].str.contains(search_term, case=False, na=False) | 
                       df['Student ID'].str.contains(search_term, case=False, na=False)]
                
                if df.empty:
                    st.warning("🔍 No student found with that name or ID.")
                else:
                    st.success(f"🎯 Found {len(df)} student(s) matching your search.")
            else:
                st.info("🔍 Please enter a student name or ID to search.")
                df = df.iloc[0:0]  # Empty dataframe
        
        else:  # Due/Overdue Students Only
            from datetime import timedelta
            next_7_days = datetime.now() + timedelta(days=7)
            df = df[(df['Status'] == 'Expired') | (pd.to_datetime(df['Expiry Date']) <= next_7_days)]
            
            if df.empty:
                st.success("🎉 No students have due or overdue payments!")
            else:
                st.warning(f"⚠️ {len(df)} students require payment processing.")
        
        # Display students for payment processing
        if not df.empty:
            for _, student in df.iterrows():
                emoji = get_instrument_emoji(student['Instrument'])
                status_icon = "🔴" if student['Status'] == 'Expired' else "🟢"
                with st.expander(f"{status_icon} {emoji} {student['Full Name']} - {student['Student ID']} ({student['Status']})"):
                    # Student Info Section
                    st.markdown("#### 📊 Student Information")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Current Plan", student['Class Plan'])
                        st.metric("Classes Progress", f"{student['Classes Completed']}/{student['Total Classes']}")
                    
                    with col2:
                        expiry_formatted = datetime.strptime(str(student['Expiry Date']).split(' ')[0], '%Y-%m-%d').strftime('%d-%m-%Y')
                        st.metric("Expiry Date", expiry_formatted)
                        st.metric("Mobile", student['Mobile'])
                    
                    with col3:
                        default_email = student.get('Email', 'N/A')
                        st.metric("Email", default_email)
                        st.metric("Instrument", student['Instrument'])
                    
                    st.divider()
                    
                    # Payment Processing Section
                    st.markdown("#### 💰 Payment Processing")
                    
                    # WhatsApp reminder for overdue students
                    if student['Status'] == 'Expired':
                        if st.button(f"📱 Send WhatsApp Reminder", key=f"wa_{student['Student ID']}", use_container_width=True):
                            success, message = send_whatsapp_reminder(
                                student['Mobile'], student['Full Name'], 
                                student['Class Plan'], student['Expiry Date']
                            )
                            if success:
                                st.success("Reminder sent!")
                            else:
                                st.error("Failed to send")
                        st.divider()
                    
                    # Payment form outside to enable real-time updates
                    # Payment details in organized columns
                    pcol1, pcol2 = st.columns(2)
                    
                    with pcol1:
                        amount = st.number_input("💵 Amount (₹)", min_value=0.0, key=f"amt_{student['Student ID']}")
                        
                        # Auto-populate email
                        default_email = student.get('Email', '') or ''
                        student_email = st.text_input("📧 Student Email", value=default_email, key=f"email_{student['Student ID']}")
                        
                        payment_method = st.selectbox(
                            "💳 Payment Method",
                            ["Cash Payment", "UPI Payment", "Card Payment"],
                            key=f"method_{student['Student ID']}"
                        )
                    
                    with pcol2:
                        # Payment plan selection
                        payment_plan = st.selectbox(
                            "📅 New Payment Plan",
                            ["1 Month - 8", "3 Month - 24", "6 Month - 48", "12 Month - 96"],
                            index=0,
                            key=f"plan_{student['Student ID']}"
                        )
                        
                        # Calculate next due date (real-time update)
                        from datetime import timedelta
                        current_expiry = datetime.strptime(str(student['Expiry Date']).split(' ')[0], '%Y-%m-%d')
                        package_days = {"1 Month - 8": 30, "3 Month - 24": 90, "6 Month - 48": 180, "12 Month - 96": 365}
                        plan_days = package_days[payment_plan]
                        calculated_next_due = current_expiry + timedelta(days=plan_days)
                        
                        next_due_date = st.date_input(
                            "🗓️ Next Due Date (Auto-calculated, Editable)", 
                            value=calculated_next_due.date(),
                            key=f"due_{student['Student ID']}"
                        )
                    
                    # Receipt and calculation info
                    st.markdown("---")
                    
                    # System generated receipt number
                    conn = sqlite3.connect('chords_crm.db')
                    cursor = conn.cursor()
                    cursor.execute('SELECT COUNT(*) FROM payments')
                    receipt_count = cursor.fetchone()[0]
                    conn.close()
                    
                    receipt_no = f"CMA{receipt_count + 1:05d}"
                    
                    rcol1, rcol2 = st.columns(2)
                    with rcol1:
                        st.info(f"📄 **Receipt:** {receipt_no}")
                    with rcol2:
                        st.info(f"📅 **Plan:** {payment_plan.split(' - ')[0]} ({plan_days} days)")
                    
                    # Submit button
                    if st.button("✅ Process Payment", use_container_width=True, type="primary", key=f"submit_{student['Student ID']}"):
                        if amount and student_email:
                            # Update database
                            conn = sqlite3.connect('chords_crm.db')
                            cursor = conn.cursor()
                            cursor.execute("UPDATE students SET expiry_date = ?, class_plan = ? WHERE student_id = ?", 
                                         (next_due_date.strftime('%Y-%m-%d'), payment_plan, student['Student ID']))
                            
                            cursor.execute('''
                                INSERT INTO payments (student_id, amount, payment_date, receipt_number)
                                VALUES (?, ?, ?, ?)
                            ''', (student['Student ID'], amount, datetime.now().strftime('%Y-%m-%d'), receipt_no))
                            
                            conn.commit()
                            conn.close()
                            
                            # Send receipt
                            with st.spinner("📧 Sending receipt..."):
                                success, message = send_payment_receipt_email(
                                    student_email, student['Full Name'], 
                                    amount, receipt_no, payment_plan,
                                    student['Student ID'], student['Instrument'],
                                    str(student['Start Date']).split(' ')[0], next_due_date.strftime('%Y-%m-%d'),
                                    payment_method
                                )
                                if success:
                                    st.success("✅ Payment processed successfully! Receipt sent via email.")
                                    st.rerun()
                                else:
                                    st.error(f"❌ Failed to send receipt: {message}")
                        else:
                            st.error("⚠️ Please fill in amount and email address")
    else:
        st.info("📅 No students registered yet.")
        
    # Payment summary stats
    if students:
        st.markdown("---")
        st.markdown("### 📊 Payment Overview")
        
        # Calculate overall stats
        all_df = pd.DataFrame(students, columns=[
            'ID', 'Student ID', 'Full Name', 'Age', 'Mobile', 'Instrument', 'Class Plan', 
            'Total Classes', 'Start Date', 'Expiry Date', 'Status', 'Classes Completed', 
            'Extra Classes', 'First Class Date', 'Email', 'Date of Birth', 'Sex'
        ])
        all_df['Expiry Date'] = all_df['Expiry Date'].astype(str).str.split(' ').str[0]
        all_df['Status'] = all_df.apply(lambda row: 
            'Expired' if datetime.strptime(row['Expiry Date'], '%Y-%m-%d') < datetime.now()
            else 'Active', axis=1)
        
        from datetime import timedelta
        next_7_days = datetime.now() + timedelta(days=7)
        due_soon = len(all_df[pd.to_datetime(all_df['Expiry Date']) <= next_7_days])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            expired_count = len(all_df[all_df['Status'] == 'Expired'])
            st.metric("🔴 Overdue Payments", expired_count)
        with col2:
            st.metric("⚠️ Due in 7 Days", due_soon)
        with col3:
            st.metric("💰 Total Students", len(all_df))
    
    if st.button("← Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()

# Student list and edit module
def student_list_module():
    display_header("Student List & Edit")
    
    students = get_all_students()
    if students:
        df = pd.DataFrame(students, columns=[
            'ID', 'Student ID', 'Full Name', 'Age', 'Mobile', 'Instrument', 'Class Plan', 
            'Total Classes', 'Start Date', 'Expiry Date', 'Status', 'Classes Completed', 
            'Extra Classes', 'First Class Date', 'Email', 'Date of Birth', 'Sex'
        ])
        
        # Convert date columns to datetime (clean time component first)
        df['Start Date'] = df['Start Date'].astype(str).str.split(' ').str[0]
        df['Expiry Date'] = df['Expiry Date'].astype(str).str.split(' ').str[0]
        df['Start Date'] = pd.to_datetime(df['Start Date'])
        df['Expiry Date'] = pd.to_datetime(df['Expiry Date'])
        
        # Make student data editable
        edited_df = st.data_editor(
            df[['Student ID', 'Full Name', 'Age', 'Mobile', 'Instrument', 'Class Plan', 'Start Date', 'Expiry Date']],
            column_config={
                "Student ID": st.column_config.TextColumn("Student ID", disabled=True),
                "Full Name": st.column_config.TextColumn("Full Name"),
                "Age": st.column_config.NumberColumn("Age", min_value=1, max_value=100),
                "Mobile": st.column_config.TextColumn("Mobile"),
                "Instrument": st.column_config.SelectboxColumn(
                    "Instrument",
                    options=["Keyboard", "Piano", "Guitar", "Drums", "Violin", "Flute", "Carnatic Vocals", "Hindustani Vocals", "Western Vocals"]
                ),
                "Class Plan": st.column_config.SelectboxColumn(
                    "Class Plan",
                    options=["1 Month - 8", "3 Month - 24", "6 Month - 48", "12 Month - 96"]
                ),
                "Start Date": st.column_config.DateColumn("Start Date", format="DD-MM-YYYY"),
                "Expiry Date": st.column_config.DateColumn("Expiry Date", format="DD-MM-YYYY")
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Action buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💾 Save Changes", use_container_width=True):
                conn = sqlite3.connect('chords_crm.db')
                cursor = conn.cursor()
                
                for idx, row in edited_df.iterrows():
                    cursor.execute('''
                        UPDATE students SET 
                            full_name = ?, age = ?, mobile = ?, instrument = ?, 
                            class_plan = ?, start_date = ?, expiry_date = ?
                        WHERE student_id = ?
                    ''', (row['Full Name'], row['Age'], row['Mobile'], row['Instrument'],
                         row['Class Plan'], str(row['Start Date']), str(row['Expiry Date']), row['Student ID']))
                
                conn.commit()
                conn.close()
                st.success("✅ Student information updated successfully!")
                st.rerun()
        
        with col2:
            if st.button("🗑️ Delete Student", use_container_width=True, type="secondary"):
                st.session_state.show_delete_form = True
                st.rerun()
        
        # Delete student form
        if st.session_state.get('show_delete_form', False):
            st.markdown("---")
            st.markdown("### ⚠️ Delete Student")
            
            # Student selection for deletion
            student_options = [f"{row['Student ID']} - {row['Full Name']}" for _, row in df.iterrows()]
            selected_student = st.selectbox("👥 Select Student to Delete:", student_options)
            
            if selected_student:
                student_id = selected_student.split(' - ')[0]
                student_name = selected_student.split(' - ')[1]
                
                st.error(f"⚠️ You are about to delete: **{student_name} ({student_id})**")
                st.warning("🚨 This action cannot be undone! All student data, attendance records, and payment history will be permanently deleted.")
                
                # Confirmation
                confirm_text = st.text_input("Type 'DELETE' to confirm:", key="delete_confirm")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("❌ Cancel", use_container_width=True):
                        st.session_state.show_delete_form = False
                        st.rerun()
                
                with col3:
                    if st.button("🗑️ Confirm Delete", use_container_width=True, type="primary"):
                        if confirm_text == "DELETE":
                            # Delete from all related tables
                            conn = sqlite3.connect('chords_crm.db')
                            cursor = conn.cursor()
                            
                            # Delete from attendance table
                            cursor.execute('DELETE FROM attendance WHERE student_id = ?', (student_id,))
                            
                            # Delete from payments table
                            cursor.execute('DELETE FROM payments WHERE student_id = ?', (student_id,))
                            
                            # Delete from students table
                            cursor.execute('DELETE FROM students WHERE student_id = ?', (student_id,))
                            
                            conn.commit()
                            conn.close()
                            
                            st.success(f"✅ Student {student_name} ({student_id}) deleted successfully!")
                            st.session_state.show_delete_form = False
                            st.rerun()
                        else:
                            st.error("Please type 'DELETE' to confirm deletion.")
    
    else:
        st.info("No students registered yet.")
    
    if st.button("← Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()

# Due alerts module
def due_alerts_module():
    display_header("Due Alerts - Next 3 Days & Overdue")
    
    students = get_all_students()
    if students:
        df = pd.DataFrame(students, columns=[
            'ID', 'Student ID', 'Full Name', 'Age', 'Mobile', 'Instrument', 'Class Plan', 
            'Total Classes', 'Start Date', 'Expiry Date', 'Status', 'Classes Completed', 
            'Extra Classes', 'First Class Date', 'Email', 'Date of Birth', 'Sex'
        ])
        
        from datetime import timedelta
        today = datetime.now()
        next_3_days = today + timedelta(days=3)
        
        # Clean and parse expiry dates
        df['Expiry Date'] = df['Expiry Date'].astype(str).str.split(' ').str[0]  # Remove time part
        df['Expiry Date Parsed'] = pd.to_datetime(df['Expiry Date'])
        
        overdue_df = df[df['Expiry Date Parsed'] < today]
        due_soon_df = df[(df['Expiry Date Parsed'] >= today) & (df['Expiry Date Parsed'] <= next_3_days)]
        
        # Overdue students
        if not overdue_df.empty:
            st.markdown("### 🔴 Overdue Students")
            for _, student in overdue_df.iterrows():
                days_overdue = (today - student['Expiry Date Parsed']).days
                emoji = get_instrument_emoji(student['Instrument'])
                
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"""
                    <div class="overdue-alert">
                        <strong>{emoji} {student['Full Name']} - {student['Student ID']}</strong><br>
                        Plan: {student['Class Plan']} | Mobile: {student['Mobile']}<br>
                        <strong>Overdue by {days_overdue} days</strong> (Expired: {datetime.strptime(student['Expiry Date'], '%Y-%m-%d').strftime('%d-%m-%Y')})
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if st.button("📱 WhatsApp", key=f"wa_overdue_{student['Student ID']}"):
                        success, message = send_whatsapp_reminder(
                            student['Mobile'], student['Full Name'], 
                            student['Class Plan'], student['Expiry Date']
                        )
                        if success:
                            st.success("Reminder sent!")
                        else:
                            st.error("Failed to send")
        
        # Due in next 3 days
        if not due_soon_df.empty:
            st.markdown("### 🟡 Due in Next 3 Days")
            for _, student in due_soon_df.iterrows():
                days_left = (student['Expiry Date Parsed'] - today).days
                emoji = get_instrument_emoji(student['Instrument'])
                
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"""
                    <div class="success-alert">
                        <strong>{emoji} {student['Full Name']} - {student['Student ID']}</strong><br>
                        Plan: {student['Class Plan']} | Mobile: {student['Mobile']}<br>
                        <strong>Due in {days_left} days</strong> (Expires: {datetime.strptime(student['Expiry Date'], '%Y-%m-%d').strftime('%d-%m-%Y')})
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if st.button("📱 WhatsApp", key=f"wa_due_{student['Student ID']}"):
                        success, message = send_whatsapp_reminder(
                            student['Mobile'], student['Full Name'], 
                            student['Class Plan'], student['Expiry Date']
                        )
                        if success:
                            st.success("Reminder sent!")
                        else:
                            st.error("Failed to send")
        
        if overdue_df.empty and due_soon_df.empty:
            st.success("🎉 No students are overdue or due in the next 3 days!")
    
    else:
        st.info("No students registered yet.")
    
    if st.button("← Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()

# Main app
def main():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if 'page' not in st.session_state:
        st.session_state.page = "dashboard"
    
    if not st.session_state.logged_in:
        login()
    else:
        # Sidebar logout
        with st.sidebar:
            st.write("Logged in as: **admin**")
            if st.button("Logout"):
                st.session_state.logged_in = False
                st.session_state.page = "dashboard"
                st.rerun()
        
        # Page routing
        if st.session_state.page == "dashboard":
            dashboard()
        elif st.session_state.page == "registration":
            student_registration()
        elif st.session_state.page == "attendance":
            attendance_module()
        elif st.session_state.page == "biometric":
            biometric_enrollment()
        elif st.session_state.page == "reports":
            reports_module()
        elif st.session_state.page == "payments":
            payment_module()
        elif st.session_state.page == "due_alerts":
            due_alerts_module()
        elif st.session_state.page == "student_list":
            student_list_module()
        # Security page removed

if __name__ == "__main__":
    main()