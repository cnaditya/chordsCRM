import streamlit as st
import pandas as pd
from datetime import datetime, date
import sqlite3
from database import init_db, add_student, mark_attendance, get_all_students, get_dashboard_stats
from mantra_simple import mantra_scanner as scanner
from sms_email import send_whatsapp_reminder, send_payment_receipt_email, send_whatsapp_payment_receipt, send_sms_receipt
from style import apply_custom_css, get_instrument_emoji, display_header, display_metric_card, display_section_header
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
    display_header("Chords Music Academy", "Comprehensive Student Management System")
    
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
    
    # Navigation Grid - Fixed alignment
    col1, col2, col3 = st.columns(3, gap="large")
    
    with col1:
        st.markdown("""
        <div class="nav-card" style="height: 220px; padding: 1.5rem;">
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
        <div class="nav-card" style="height: 220px; padding: 1.5rem;">
            <div class="nav-card-icon">📈</div>
            <div class="nav-card-title">Operations Management</div>
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
        <div class="nav-card" style="height: 220px; padding: 1.5rem;">
            <div class="nav-card-icon">💰</div>
            <div class="nav-card-title">Financial Management</div>
            <div class="nav-card-desc">Payment processing and financial reports</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("💰 Payment Processing", use_container_width=True):
            st.session_state.page = "payments"
            st.rerun()
        if st.button("📊 Analytics & Reports", use_container_width=True):
            st.session_state.page = "reports"
            st.rerun()
    
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
    
    # Use form container to ensure proper input handling
    with st.form("student_registration_form"):
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
        
        # Submit button inside form
        submitted = st.form_submit_button("Register Student", type="primary")
    # Form processing
    if submitted:
        if full_name.strip() and mobile.strip() and email.strip():
            student_id = add_student(full_name, age, mobile, email, 
                                   date_of_birth.strftime('%Y-%m-%d'), sex, instrument,
                                   "No Package", start_date.strftime('%Y-%m-%d'))  # No package initially
            
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
        # Create DataFrame with actual database columns
        df = pd.DataFrame(students, columns=[
            'ID', 'Student ID', 'Full Name', 'Age', 'Mobile', 'Email', 'Date of Birth', 'Sex',
            'Instrument', 'Class Plan', 'Total Classes', 'Start Date', 'Expiry Date', 'Status', 
            'Classes Completed', 'Extra Classes', 'First Class Date', 'Created At', 'Updated At'
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
            try:
                df = df[(df['Status'] == 'Expired') | (pd.to_datetime(df['Expiry Date'], errors='coerce') <= next_7_days)]
            except Exception as e:
                st.error(f"Date parsing error: {str(e)}")
                df = df[df['Status'] == 'Expired']  # Fallback to only expired students
            
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
                        try:
                            expiry_formatted = datetime.strptime(str(student['Expiry Date']).split(' ')[0], '%Y-%m-%d').strftime('%d-%m-%Y')
                        except:
                            expiry_formatted = str(student['Expiry Date']).split(' ')[0]
                        st.metric("Expiry Date", expiry_formatted)
                        st.metric("Mobile", student['Mobile'])
                    
                    with col3:
                        default_email = student.get('Email', 'N/A')
                        st.metric("Email", default_email)
                        st.metric("Instrument", student['Instrument'])
                    
                    st.divider()
                    
                    # Payment Processing Section
                    st.markdown("#### 💰 Payment Processing")
                    
                    # Calculate payment summary
                    conn = sqlite3.connect('chords_crm.db')
                    cursor = conn.cursor()
                    cursor.execute('SELECT SUM(amount) FROM payments WHERE student_id = ?', (student['Student ID'],))
                    total_paid = cursor.fetchone()[0] or 0
                    conn.close()
                    
                    # Chords Music Academy Fee Structure
                    default_package_fees = {
                        "1 Month - 8": 4000,
                        "3 Month - 24": 10800,  # 10% off
                        "6 Month - 48": 20400,  # 15% off
                        "12 Month - 96": 38400, # 20% off
                        "No Package": 0
                    }
                    
                    # Editable package fee (for bargaining)
                    default_fee = default_package_fees.get(student['Class Plan'], 0)
                    total_fees = st.number_input(
                        f"📋 Package Fee for {student['Class Plan']}",
                        min_value=0.0,
                        value=float(default_fee),
                        step=100.0,
                        help="Default fee - can be edited for discounts/bargaining",
                        key=f"package_fee_{student['Student ID']}"
                    )
                    
                    # total_fees is now set above as editable input
                    pending_amount = max(0, total_fees - total_paid)
                    
                    # Payment Summary
                    st.markdown("**💳 Payment Summary**")
                    pcol1, pcol2, pcol3 = st.columns(3)
                    with pcol1:
                        st.metric("📊 Total Fees", f"₹{total_fees:,.0f}")
                    with pcol2:
                        st.metric("✅ Paid Amount", f"₹{total_paid:,.0f}")
                    with pcol3:
                        if pending_amount > 0:
                            st.metric("⚠️ Pending Amount", f"₹{pending_amount:,.0f}")
                        else:
                            st.metric("🎉 Status", "Fully Paid")
                    
                    st.divider()
                    
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
                        # Suggest pending amount but allow custom amount
                        suggested_amount = min(pending_amount, pending_amount) if pending_amount > 0 else 0
                        amount = st.number_input("💵 Payment Amount (₹)", 
                                               min_value=0.0, 
                                               value=float(suggested_amount),
                                               key=f"amt_{student['Student ID']}")
                        
                        # Show remaining after this payment
                        if amount > 0:
                            remaining_after_payment = max(0, pending_amount - amount)
                            if remaining_after_payment > 0:
                                st.info(f"💡 Remaining after payment: ₹{remaining_after_payment:,.0f}")
                            else:
                                st.success("🎉 Package will be fully paid!")
                        
                        # Auto-populate email
                        default_email = student.get('Email', '') or ''
                        student_email = st.text_input("📧 Student Email", value=default_email, key=f"email_{student['Student ID']}")
                        
                        payment_method = st.selectbox(
                            "💳 Payment Method",
                            ["Cash Payment", "UPI Payment", "Card Payment"],
                            key=f"method_{student['Student ID']}"
                        )
                    
                    with pcol2:
                        # Show current package (read-only)
                        st.text_input("📅 Current Package", value=student['Class Plan'], disabled=True, key=f"current_plan_{student['Student ID']}")
                        
                        # Payment status selection
                        payment_status = st.radio(
                            "💰 Payment Status",
                            ["Installment Payment", "Fully Paid - No Dues"],
                            key=f"status_{student['Student ID']}"
                        )
                        
                        # Next payment due date (for both installments and renewals)
                        from datetime import timedelta
                        if payment_status == "Installment Payment":
                            default_next_due = datetime.now() + timedelta(days=30)  # Default 1 month
                            help_text = "Set when the next installment is due"
                        else:
                            # For fully paid students, set renewal date
                            default_next_due = datetime.now() + timedelta(days=365)  # Default 1 year for renewal
                            help_text = "Set when this student needs to renew (next package start date)"
                        
                        next_payment_due = st.date_input(
                            "🗓️ Next Due Date", 
                            value=default_next_due.date(),
                            help=help_text,
                            key=f"next_due_{student['Student ID']}"
                        )
                        
                        if payment_status == "Fully Paid - No Dues":
                            st.info("💡 This date will be used for renewal reminders")
                        
                        # Payment notes
                        payment_notes = st.text_area(
                            "📝 Payment Notes",
                            placeholder="e.g., First installment of 3, Next due in 2 months",
                            key=f"notes_{student['Student ID']}"
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
                        st.info(f"📅 **Package:** {student['Class Plan']}")
                    
                    # Payment processing buttons
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("💰 Process Payment & Send Email", use_container_width=True, type="primary", key=f"process_email_{student['Student ID']}"):
                            if amount > 0 and student_email:
                                conn = sqlite3.connect('chords_crm.db')
                                cursor = conn.cursor()
                                next_due_str = next_payment_due.strftime('%Y-%m-%d')
                                cursor.execute('''
                                    INSERT INTO payments (student_id, amount, payment_date, receipt_number, notes, next_due_date)
                                    VALUES (?, ?, ?, ?, ?, ?)
                                ''', (student['Student ID'], amount, datetime.now().strftime('%Y-%m-%d'), 
                                     receipt_no, payment_notes, next_due_str))
                                conn.commit()
                                conn.close()
                                
                                email_success, email_message = send_payment_receipt_email(
                                    student_email, student['Full Name'], 
                                    amount, receipt_no, student['Class Plan'],
                                    student['Student ID'], student['Instrument'],
                                    str(student['Start Date']).split(' ')[0], str(student['Expiry Date']).split(' ')[0],
                                    payment_method, next_due_str
                                )
                                
                                if email_success:
                                    st.success(f"✅ Payment ₹{amount} recorded & Email sent! Receipt: {receipt_no}")
                                else:
                                    st.success(f"✅ Payment ₹{amount} recorded! Receipt: {receipt_no}")
                                    st.error(f"❌ Email failed: {email_message}")
                                st.rerun()
                            else:
                                if amount <= 0:
                                    st.error("⚠️ Please enter payment amount")
                                if not student_email:
                                    st.error("⚠️ Please enter email address")
                    
                    with col2:
                        if st.button("💰 Process Payment & Send WhatsApp", use_container_width=True, type="primary", key=f"process_whatsapp_{student['Student ID']}"):
                            if amount > 0:
                                conn = sqlite3.connect('chords_crm.db')
                                cursor = conn.cursor()
                                next_due_str = next_payment_due.strftime('%Y-%m-%d')
                                cursor.execute('''
                                    INSERT INTO payments (student_id, amount, payment_date, receipt_number, notes, next_due_date)
                                    VALUES (?, ?, ?, ?, ?, ?)
                                ''', (student['Student ID'], amount, datetime.now().strftime('%Y-%m-%d'), 
                                     receipt_no, payment_notes, next_due_str))
                                conn.commit()
                                conn.close()
                                
                                next_due_info = f"Next Due: {next_payment_due.strftime('%d-%m-%Y')}" if next_payment_due else "🎉 Fully Paid - No Dues!"
                                
                                # Send WhatsApp receipt to student
                                whatsapp_success, whatsapp_message = send_whatsapp_payment_receipt(
                                    student['Mobile'], student['Full Name'],
                                    amount, receipt_no, student['Class Plan'],
                                    datetime.now().strftime('%Y-%m-%d'), next_due_info
                                )
                                
                                if whatsapp_success:
                                    st.success(f"✅ Payment ₹{amount} recorded & WhatsApp sent! Receipt: {receipt_no}")
                                    st.info(f"Sent to: {student['Mobile']} | Amount: ₹{amount}")
                                else:
                                    st.success(f"✅ Payment ₹{amount} recorded! Receipt: {receipt_no}")
                                    st.error(f"❌ WhatsApp failed: {whatsapp_message}")
                                st.rerun()
                            else:
                                st.error("⚠️ Please enter payment amount")
    else:
        st.info("📅 No students registered yet.")
        
    # Payment summary stats
    if students:
        st.markdown("---")
        st.markdown("### 📊 Payment Overview")
        
        # Calculate overall stats
        all_df = pd.DataFrame(students, columns=[
            'ID', 'Student ID', 'Full Name', 'Age', 'Mobile', 'Email', 'Date of Birth', 'Sex',
            'Instrument', 'Class Plan', 'Total Classes', 'Start Date', 'Expiry Date', 'Status', 
            'Classes Completed', 'Extra Classes', 'First Class Date', 'Created At', 'Updated At'
        ])
        all_df['Expiry Date'] = all_df['Expiry Date'].astype(str).str.split(' ').str[0]
        
        def get_status_safe(row):
            try:
                if row['Expiry Date'] and '-' in str(row['Expiry Date']):
                    return 'Expired' if datetime.strptime(row['Expiry Date'], '%Y-%m-%d') < datetime.now() else 'Active'
                else:
                    return 'Active'
            except:
                return 'Active'
        
        all_df['Status'] = all_df.apply(get_status_safe, axis=1)
        
        from datetime import timedelta
        next_7_days = datetime.now() + timedelta(days=7)
        
        # Safe date conversion with null handling
        try:
            valid_dates = pd.to_datetime(all_df['Expiry Date'], errors='coerce')
            valid_dates = valid_dates.dropna()  # Remove invalid dates
            due_soon = len(all_df[valid_dates <= next_7_days]) if not valid_dates.empty else 0
        except:
            due_soon = 0
        
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
    display_header("Student Management", "Search, Edit & Manage Student Records")
    
    students = get_all_students()
    if not students:
        st.info("No students registered yet.")
        if st.button("← Back to Dashboard"):
            st.session_state.page = "dashboard"
            st.rerun()
        return
    
    df = pd.DataFrame(students, columns=[
        'ID', 'Student ID', 'Full Name', 'Age', 'Mobile', 'Email', 'Date of Birth', 'Sex',
        'Instrument', 'Class Plan', 'Total Classes', 'Start Date', 'Expiry Date', 'Status', 
        'Classes Completed', 'Extra Classes', 'First Class Date', 'Created At', 'Updated At'
    ])
    
    # Search section
    st.markdown("### 🔍 Find Student")
    col1, col2 = st.columns(2)
    
    with col1:
        search_term = st.text_input("🔍 Search by Name or ID", placeholder="Enter student name or ID")
    
    with col2:
        if 'show_all_students' not in st.session_state:
            st.session_state.show_all_students = False
        
        if not st.session_state.show_all_students:
            if st.button("📊 Show All Students", use_container_width=True):
                st.session_state.show_all_students = True
                st.rerun()
        else:
            if st.button("❌ Hide All Students", use_container_width=True):
                st.session_state.show_all_students = False
                st.rerun()
    
    # Apply search
    if search_term or st.session_state.get('show_all_students', False):
        if st.session_state.get('show_all_students', False) and not search_term:
            filtered_df = df.copy()
            st.info(f"📊 Showing all {len(filtered_df)} students")
        else:
            filtered_df = df[df['Full Name'].str.contains(search_term, case=False, na=False) | 
                           df['Student ID'].str.contains(search_term, case=False, na=False)]
            if filtered_df.empty:
                st.warning("🔍 No students found matching your search.")
                return
            else:
                st.info(f"📊 Found {len(filtered_df)} student(s)")
        
        # Display students
        st.markdown("### 👥 Student Records")
        
        for _, student in filtered_df.iterrows():
            emoji = get_instrument_emoji(student['Instrument'])
            
            # Calculate status
            if student['Class Plan'] == 'No Package':
                status = 'No Package'
                status_color = "⚪"
            else:
                try:
                    expiry_date = pd.to_datetime(str(student['Expiry Date']).split(' ')[0])
                    status = 'Expired' if expiry_date < pd.Timestamp.now() else 'Active'
                    status_color = "🔴" if status == 'Expired' else "🟢"
                except:
                    status = 'No Package'
                    status_color = "⚪"
            
            with st.expander(f"{status_color} {emoji} {student['Full Name']} - {student['Student ID']} ({status})"):
                # Basic info
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("**📋 Basic Info**")
                    st.text(f"Name: {student['Full Name']}")
                    try:
                        age_display = str(int(student['Age'])) if student['Age'] is not None else 'N/A'
                    except (ValueError, TypeError):
                        age_display = 'N/A'
                    st.text(f"Age: {age_display}")
                    st.text(f"Mobile: {student['Mobile']}")
                
                with col2:
                    st.markdown("**🎵 Course Info**")
                    st.text(f"Instrument: {student['Instrument']}")
                    st.text(f"Package: {student['Class Plan']}")
                    st.text(f"Classes: {student['Classes Completed']}/{student['Total Classes']}")
                
                with col3:
                    st.markdown("**📅 Dates**")
                    start_date = str(student['Start Date']).split(' ')[0]
                    try:
                        st.text(f"Start: {pd.to_datetime(start_date).strftime('%d-%m-%Y')}")
                    except:
                        st.text(f"Start: {start_date}")
                    
                    if student['Class Plan'] != 'No Package':
                        expiry_date = str(student['Expiry Date']).split(' ')[0]
                        try:
                            st.text(f"Expiry: {pd.to_datetime(expiry_date).strftime('%d-%m-%Y')}")
                        except:
                            st.text(f"Expiry: {expiry_date}")
                    else:
                        st.text("Expiry: No Package")
                
                st.divider()
                
                # Edit form
                st.markdown("**✏️ Edit Student**")
                
                ecol1, ecol2 = st.columns(2)
                
                with ecol1:
                    new_name = st.text_input("Full Name", value=student['Full Name'], key=f"name_{student['Student ID']}")
                    try:
                        age_value = int(student['Age']) if student['Age'] is not None else 18
                    except (ValueError, TypeError):
                        age_value = 18
                    new_age = st.number_input("Age", value=age_value, min_value=1, max_value=100, key=f"age_{student['Student ID']}")
                    new_mobile = st.text_input("Mobile", value=student['Mobile'], key=f"mobile_{student['Student ID']}")
                
                with ecol2:
                    instruments_list = ["Keyboard", "Piano", "Guitar", "Drums", "Violin", "Flute", "Carnatic Vocals", "Hindustani Vocals", "Western Vocals"]
                    try:
                        current_index = instruments_list.index(student['Instrument'])
                    except ValueError:
                        current_index = 0  # Default to first instrument if not found
                    new_instrument = st.selectbox("Instrument", 
                                                instruments_list,
                                                index=current_index,
                                                key=f"inst_{student['Student ID']}")
                    
                    packages_list = ["No Package", "1 Month - 8", "3 Month - 24", "6 Month - 48", "12 Month - 96"]
                    try:
                        package_index = packages_list.index(student['Class Plan'])
                    except ValueError:
                        package_index = 0  # Default to first package if not found
                    new_package = st.selectbox("Package", 
                                             packages_list,
                                             index=package_index,
                                             key=f"pkg_{student['Student ID']}")
                    
                    try:
                        start_value = pd.to_datetime(start_date).date()
                    except:
                        start_value = datetime.now().date()
                    
                    new_start_date = st.date_input("Start Date", 
                                                  value=start_value,
                                                  key=f"start_{student['Student ID']}")
                
                # Action buttons
                bcol1, bcol2 = st.columns(2)
                
                with bcol1:
                    if st.button("💾 Save Changes", key=f"save_{student['Student ID']}", use_container_width=True, type="primary"):
                        conn = sqlite3.connect('chords_crm.db')
                        cursor = conn.cursor()
                        
                        # Calculate expiry date
                        if new_package != "No Package":
                            from datetime import timedelta
                            package_days = {"1 Month - 8": 30, "3 Month - 24": 90, "6 Month - 48": 180, "12 Month - 96": 365}
                            calculated_expiry = new_start_date + timedelta(days=package_days[new_package])
                            expiry_str = calculated_expiry.strftime('%Y-%m-%d')
                        else:
                            expiry_str = new_start_date.strftime('%Y-%m-%d')
                        
                        cursor.execute('''
                            UPDATE students SET 
                                full_name = ?, age = ?, mobile = ?, instrument = ?, 
                                class_plan = ?, start_date = ?, expiry_date = ?
                            WHERE student_id = ?
                        ''', (new_name, new_age, new_mobile, new_instrument,
                             new_package, new_start_date.strftime('%Y-%m-%d'), expiry_str, student['Student ID']))
                        
                        conn.commit()
                        conn.close()
                        st.success("✅ Student updated successfully!")
                        st.rerun()
                
                with bcol2:
                    if st.button("🗑️ Delete Student", key=f"del_{student['Student ID']}", use_container_width=True, type="secondary"):
                        st.session_state[f"confirm_delete_{student['Student ID']}"] = True
                        st.rerun()
                
                # Delete confirmation
                if st.session_state.get(f"confirm_delete_{student['Student ID']}", False):
                    st.error(f"⚠️ Delete {student['Full Name']} ({student['Student ID']})? This cannot be undone!")
                    dcol1, dcol2 = st.columns(2)
                    
                    with dcol1:
                        if st.button("❌ Cancel", key=f"cancel_{student['Student ID']}"):
                            del st.session_state[f"confirm_delete_{student['Student ID']}"]
                            st.rerun()
                    
                    with dcol2:
                        if st.button("🗑️ Confirm Delete", key=f"confirm_{student['Student ID']}", type="primary"):
                            conn = sqlite3.connect('chords_crm.db')
                            cursor = conn.cursor()
                            
                            cursor.execute('DELETE FROM attendance WHERE student_id = ?', (student['Student ID'],))
                            cursor.execute('DELETE FROM payments WHERE student_id = ?', (student['Student ID'],))
                            cursor.execute('DELETE FROM students WHERE student_id = ?', (student['Student ID'],))
                            
                            conn.commit()
                            conn.close()
                            
                            st.success(f"✅ {student['Full Name']} deleted successfully!")
                            del st.session_state[f"confirm_delete_{student['Student ID']}"]
                            st.rerun()
    
    else:
        st.info("🔍 Enter search criteria to view student records")
    
    if st.button("← Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()

# Old broken function - keeping for reference
def student_list_module_old():
    display_header("Student Management", "Search, Edit & Manage Student Records")
    
    students = get_all_students()
    if students:
        df = pd.DataFrame(students, columns=[
            'ID', 'Student ID', 'Full Name', 'Age', 'Mobile', 'Instrument', 'Class Plan', 
            'Total Classes', 'Start Date', 'Expiry Date', 'Status', 'Classes Completed', 
            'Extra Classes', 'First Class Date', 'Email', 'Date of Birth', 'Sex'
        ])
        
        # Search and filter section
        st.markdown("### 🔍 Find Student")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            search_term = st.text_input("🔍 Search by Name or ID", placeholder="Enter student name or ID")
        
        with col2:
            # Get all possible instruments (not just from current students)
            all_instruments = ["Keyboard", "Piano", "Guitar", "Drums", "Violin", "Flute", "Carnatic Vocals", "Hindustani Vocals", "Western Vocals", "Carnatic Vocal"]
            current_instruments = list(df['Instrument'].unique()) if not df.empty else []
            # Combine and remove duplicates, then sort
            instruments = ['All Instruments'] + sorted(list(set(all_instruments + current_instruments)))
            instrument_filter = st.selectbox("🎼 Filter by Instrument", instruments)
        
        with col3:
            # Get all possible packages (not just from current students)
            all_packages = ["No Package", "1 Month - 8", "3 Month - 24", "6 Month - 48", "12 Month - 96"]
            current_packages = list(df['Class Plan'].unique()) if not df.empty else []
            # Combine and remove duplicates, then sort
            packages = ['All Packages'] + sorted(list(set(all_packages + current_packages)))
            package_filter = st.selectbox("📦 Filter by Package", packages)
        
        with col4:
            if 'show_students' not in st.session_state:
                st.session_state.show_students = False
            
            if not st.session_state.show_students:
                if st.button("📊 Show All Students", use_container_width=True):
                    st.session_state.show_students = True
                    st.rerun()
            else:
                if st.button("❌ Hide Students", use_container_width=True):
                    st.session_state.show_students = False
                    st.rerun()
        
        # Determine if we should show results
        should_show_results = bool(search_term) or instrument_filter != 'All Instruments' or package_filter != 'All Packages' or st.session_state.get('show_students', False)
        
        if should_show_results:
            # Apply filters
            filtered_df = df.copy()
            if search_term:
                filtered_df = filtered_df[filtered_df['Full Name'].str.contains(search_term, case=False, na=False) | 
                                        filtered_df['Student ID'].str.contains(search_term, case=False, na=False)]
            
            if instrument_filter != 'All Instruments':
                filtered_df = filtered_df[filtered_df['Instrument'] == instrument_filter]
            
            if package_filter != 'All Packages':
                filtered_df = filtered_df[filtered_df['Class Plan'] == package_filter]
        else:
            # Show nothing by default
            filtered_df = df.iloc[0:0]  # Empty dataframe
        
        if not should_show_results:
            st.info("🔍 Enter search criteria or click 'Show All Students' to view records")
        else:
            # Pagination setup
            students_per_page = 10
            total_students = len(filtered_df)
            total_pages = (total_students - 1) // students_per_page + 1 if total_students > 0 else 1
            
            # Display results count and pagination info
            if search_term or instrument_filter != 'All Instruments' or package_filter != 'All Packages':
                st.info(f"📊 Found {total_students} student(s) matching your criteria")
            else:
                st.info(f"📊 Total {total_students} students")
        
            # Pagination controls
            if total_students > students_per_page:
                col1, col2, col3 = st.columns([1, 2, 1])
                
                with col1:
                    if 'current_page' not in st.session_state:
                        st.session_state.current_page = 1
                    
                    if st.button("⬅️ Previous", disabled=st.session_state.current_page <= 1):
                        st.session_state.current_page -= 1
                        st.rerun()
                
                with col2:
                    st.markdown(f"<div style='text-align: center; padding: 0.5rem;'><strong>Page {st.session_state.current_page} of {total_pages}</strong></div>", unsafe_allow_html=True)
                
                with col3:
                    if st.button("Next ➡️", disabled=st.session_state.current_page >= total_pages):
                        st.session_state.current_page += 1
                        st.rerun()
            
            st.divider()
            
            # Display students as cards with pagination
            if not filtered_df.empty:
                # Calculate pagination
                start_idx = (st.session_state.get('current_page', 1) - 1) * students_per_page
                end_idx = start_idx + students_per_page
                page_df = filtered_df.iloc[start_idx:end_idx]
                
                st.markdown(f"### 👥 Student Records (Showing {len(page_df)} of {total_students})")
                
                for _, student in page_df.iterrows():
                    emoji = get_instrument_emoji(student['Instrument'])
                    
                    # Calculate status
                    try:
                        expiry_date = pd.to_datetime(str(student['Expiry Date']).split(' ')[0])
                        status = 'Expired' if expiry_date < pd.Timestamp.now() else 'Active'
                        status_color = "🔴" if status == 'Expired' else "🟢"
                    except:
                        status = 'No Package'
                        status_color = "⚪"
                    
                    with st.expander(f"{status_color} {emoji} {student['Full Name']} - {student['Student ID']} ({status})", expanded=False):
                        # Student info in organized layout
                        col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown("**📋 Basic Info**")
                        st.text(f"Name: {student['Full Name']}")
                        st.text(f"Age: {student['Age']}")
                        st.text(f"Mobile: {student['Mobile']}")
                        st.text(f"Email: {student.get('Email', 'N/A')}")
                    
                    with col2:
                        st.markdown("**🎵 Course Info**")
                        st.text(f"Instrument: {student['Instrument']}")
                        st.text(f"Package: {student['Class Plan']}")
                        st.text(f"Classes: {student['Classes Completed']}/{student['Total Classes']}")
                        st.text(f"Extra Classes: {student['Extra Classes']}")
                    
                    with col3:
                        st.markdown("**📅 Dates**")
                        start_date = str(student['Start Date']).split(' ')[0]
                        expiry_date = str(student['Expiry Date']).split(' ')[0]
                        st.text(f"Start: {pd.to_datetime(start_date).strftime('%d-%m-%Y')}")
                        if student['Class Plan'] != 'No Package':
                            st.text(f"Expiry: {pd.to_datetime(expiry_date).strftime('%d-%m-%Y')}")
                        else:
                            st.text("Expiry: No Package")
                    
                    st.divider()
                    
                    # Edit form for this student
                    st.markdown("**✏️ Edit Student Information**")
                    
                    ecol1, ecol2 = st.columns(2)
                    
                    with ecol1:
                        new_name = st.text_input("Full Name", value=student['Full Name'], key=f"name_{student['Student ID']}")
                        new_age = st.number_input("Age", value=int(student['Age']), min_value=1, max_value=100, key=f"age_{student['Student ID']}")
                        new_mobile = st.text_input("Mobile", value=student['Mobile'], key=f"mobile_{student['Student ID']}")
                        instruments_list = ["Keyboard", "Piano", "Guitar", "Drums", "Violin", "Flute", "Carnatic Vocals", "Hindustani Vocals", "Western Vocals"]
                        try:
                            current_index = instruments_list.index(student['Instrument'])
                        except ValueError:
                            current_index = 0  # Default to first instrument if not found
                        new_instrument = st.selectbox("Instrument", 
                                                    instruments_list,
                                                    index=current_index,
                                                    key=f"inst_{student['Student ID']}")
                    
                    with ecol2:
                        packages_list = ["No Package", "1 Month - 8", "3 Month - 24", "6 Month - 48", "12 Month - 96"]
                        try:
                            package_index = packages_list.index(student['Class Plan'])
                        except ValueError:
                            package_index = 0  # Default to first package if not found
                        new_package = st.selectbox("Package", 
                                                 packages_list,
                                                 index=package_index,
                                                 key=f"pkg_{student['Student ID']}")
                        
                        new_start_date = st.date_input("Start Date", 
                                                      value=pd.to_datetime(start_date).date(),
                                                      key=f"start_{student['Student ID']}")
                        
                        # Show calculated expiry date
                        if new_package != "No Package":
                            from datetime import timedelta
                            package_days = {"1 Month - 8": 30, "3 Month - 24": 90, "6 Month - 48": 180, "12 Month - 96": 365}
                            calculated_expiry = new_start_date + timedelta(days=package_days[new_package])
                            st.date_input("Expiry Date (Auto-calculated)", 
                                        value=calculated_expiry,
                                        disabled=True,
                                        key=f"exp_{student['Student ID']}")
                        else:
                            st.info("No expiry date for 'No Package'")
                    
                    # Action buttons
                    bcol1, bcol2, bcol3 = st.columns(3)
                    
                    with bcol1:
                        if st.button("💾 Save Changes", key=f"save_{student['Student ID']}", use_container_width=True, type="primary"):
                            conn = sqlite3.connect('chords_crm.db')
                            cursor = conn.cursor()
                            
                            # Calculate expiry date
                            if new_package != "No Package":
                                from datetime import timedelta
                                package_days = {"1 Month - 8": 30, "3 Month - 24": 90, "6 Month - 48": 180, "12 Month - 96": 365}
                                calculated_expiry = new_start_date + timedelta(days=package_days[new_package])
                                expiry_str = calculated_expiry.strftime('%Y-%m-%d')
                            else:
                                expiry_str = new_start_date.strftime('%Y-%m-%d')
                            
                            cursor.execute('''
                                UPDATE students SET 
                                    full_name = ?, age = ?, mobile = ?, instrument = ?, 
                                    class_plan = ?, start_date = ?, expiry_date = ?
                                WHERE student_id = ?
                            ''', (new_name, new_age, new_mobile, new_instrument,
                                 new_package, new_start_date.strftime('%Y-%m-%d'), expiry_str, student['Student ID']))
                            
                            conn.commit()
                            conn.close()
                            st.success("✅ Student updated successfully!")
                            st.rerun()
                    
                    with bcol3:
                        if st.button("🗑️ Delete Student", key=f"del_{student['Student ID']}", use_container_width=True, type="secondary"):
                            st.session_state[f"confirm_delete_{student['Student ID']}"] = True
                            st.rerun()
                    
                    # Delete confirmation
                    if st.session_state.get(f"confirm_delete_{student['Student ID']}", False):
                        st.error(f"⚠️ Delete {student['Full Name']} ({student['Student ID']})? This cannot be undone!")
                        dcol1, dcol2 = st.columns(2)
                        
                        with dcol1:
                            if st.button("❌ Cancel", key=f"cancel_{student['Student ID']}"):
                                del st.session_state[f"confirm_delete_{student['Student ID']}"]
                                st.rerun()
                        
                        with dcol2:
                            if st.button("🗑️ Confirm Delete", key=f"confirm_{student['Student ID']}", type="primary"):
                                conn = sqlite3.connect('chords_crm.db')
                                cursor = conn.cursor()
                                
                                cursor.execute('DELETE FROM attendance WHERE student_id = ?', (student['Student ID'],))
                                cursor.execute('DELETE FROM payments WHERE student_id = ?', (student['Student ID'],))
                                cursor.execute('DELETE FROM students WHERE student_id = ?', (student['Student ID'],))
                                
                                conn.commit()
                                conn.close()
                                
                                st.success(f"✅ {student['Full Name']} deleted successfully!")
                                del st.session_state[f"confirm_delete_{student['Student ID']}"]
                                st.rerun()
            else:
                st.warning("🔍 No students found matching your search criteria.")

    
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
            'ID', 'Student ID', 'Full Name', 'Age', 'Mobile', 'Email', 'Date of Birth', 'Sex',
            'Instrument', 'Class Plan', 'Total Classes', 'Start Date', 'Expiry Date', 'Status', 
            'Classes Completed', 'Extra Classes', 'First Class Date', 'Created At', 'Updated At'
        ])
        
        from datetime import timedelta
        today = datetime.now()
        next_3_days = today + timedelta(days=3)
        
        # Clean and parse expiry dates
        df['Expiry Date'] = df['Expiry Date'].astype(str).str.split(' ').str[0]  # Remove time part
        df['Expiry Date Parsed'] = pd.to_datetime(df['Expiry Date'], errors='coerce')
        
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
    
    # Debug section
    st.markdown("---")
    st.markdown("### 🔧 Debug WhatsApp")
    
    st.button("🧪 Test WhatsApp API", key="btn1")
    st.button("📱 Test WhatsApp Receipt", key="btn2")
    
    if st.session_state.get("btn1"):
        from sms_email import test_fast2sms
        status, response = test_fast2sms()
        st.write(f"Status: {status}")
        st.write(f"Response: {response}")
    
    if st.session_state.get("btn2"):
        success, message = send_whatsapp_payment_receipt(
            "7702031818", "Test Student", 1000, "CMA00001", 
            "1 Month - 8", datetime.now().strftime('%Y-%m-%d'), "Next Due: 01-10-2024"
        )
        if success:
            st.success(f"✅ Test successful: {message}")
        else:
            st.error(f"❌ Test failed: {message}")
    
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
