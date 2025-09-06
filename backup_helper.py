import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

def create_backup_page():
    import streamlit as st
    """Create a backup/export page for database"""
    st.header("🔄 Database Backup & Export")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Current Database Stats")
        conn = sqlite3.connect('chords_crm.db')
        
        # Get counts
        students_count = pd.read_sql_query("SELECT COUNT(*) as count FROM students", conn).iloc[0]['count']
        payments_count = pd.read_sql_query("SELECT COUNT(*) as count FROM payments", conn).iloc[0]['count']
        total_revenue = pd.read_sql_query("SELECT COALESCE(SUM(amount), 0) as total FROM payments", conn).iloc[0]['total']
        
        st.metric("Active Students", students_count)
        st.metric("Total Payments", payments_count)
        st.metric("Total Revenue", f"₹{total_revenue:,.0f}")
        
        conn.close()
    
    with col2:
        st.subheader("💾 Export Options")
        
        if st.button("📥 Download Students CSV"):
            conn = sqlite3.connect('chords_crm.db')
            
            # Based on your latest data: Aditya Palagummi, 43, 9701802225, [empty], [empty], [empty], aditya.cn@gmail.com, 22/08/82, Keyboard
            # The actual database columns seem to be: full_name, age, mobile, [empty], [empty], [empty], email, date_of_birth, instrument
            df = pd.read_sql_query("""
                SELECT 
                    full_name,
                    age,
                    mobile,
                    COALESCE(email, '') as email,
                    COALESCE(date_of_birth, '') as date_of_birth,
                    COALESCE(sex, '') as sex,
                    COALESCE(instrument, '') as instrument,
                    COALESCE(class_plan, '') as class_plan,
                    COALESCE(start_date, '') as start_date
                FROM students 
                ORDER BY full_name
            """, conn)
            conn.close()
            
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download Students Data",
                data=csv,
                file_name=f"students_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
            

        
        if st.button("📥 Download Payments CSV"):
            conn = sqlite3.connect('chords_crm.db')
            df = pd.read_sql_query("SELECT * FROM payments", conn)
            conn.close()
            
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download Payments Data",
                data=csv,
                file_name=f"payments_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    st.divider()
    
    st.subheader("📤 Bulk Upload Students")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📋 Download Template**")
        if st.button("📥 Download Student Template CSV"):
            # Create template with same columns as download
            template_data = {
                'full_name': ['John Doe', 'Jane Smith'],
                'age': [25, 22],
                'mobile': ['9876543210', '9876543211'],
                'email': ['john@example.com', 'jane@example.com'],
                'date_of_birth': ['1998-01-15', '2001-05-20'],
                'sex': ['Male', 'Female'],
                'instrument': ['Piano', 'Guitar'],
                'class_plan': ['1 Month - 8', '3 Month - 24'],
                'start_date': ['2024-01-01', '2024-01-01']
            }
            template_df = pd.DataFrame(template_data)
            csv = template_df.to_csv(index=False)
            st.download_button(
                label="Download Template",
                data=csv,
                file_name="student_upload_template.csv",
                mime="text/csv"
            )
        
        st.info("💡 Same format as downloaded data - edit and re-upload easily!")
    
    with col2:
        st.markdown("**📤 Upload Students**")
        uploaded_file = st.file_uploader("Choose CSV file", type="csv")
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                # Fill NaN values with empty strings
                df = df.fillna('')
                st.write(f"📊 Found {len(df)} students in uploaded file")
                st.dataframe(df)
                
                if st.button("✅ Upload Students", type="primary"):
                    conn = sqlite3.connect('chords_crm.db')
                    cursor = conn.cursor()
                    
                    success_count = 0
                    error_count = 0
                    
                    for _, row in df.iterrows():
                        try:
                            # Generate student ID
                            student_id = f"CMA{datetime.now().strftime('%Y%m%d%H%M%S')}{success_count:03d}"
                            
                            # Handle empty/NaN values
                            start_date_str = str(row['start_date']).strip() if row['start_date'] else ''
                            if not start_date_str or start_date_str == 'nan':
                                start_date = datetime.now()
                            else:
                                try:
                                    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                                except:
                                    try:
                                        start_date = datetime.strptime(start_date_str, '%d-%m-%Y')
                                    except:
                                        try:
                                            start_date = datetime.strptime(start_date_str, '%m/%d/%Y')
                                        except:
                                            start_date = datetime.now()
                            
                            # Parse date of birth with multiple formats
                            dob_str = str(row['date_of_birth']).strip() if row['date_of_birth'] else ''
                            if not dob_str or dob_str == 'nan':
                                dob_parsed = '2000-01-01'
                            else:
                                try:
                                    dob_parsed = datetime.strptime(dob_str, '%Y-%m-%d').strftime('%Y-%m-%d')
                                except:
                                    try:
                                        dob_parsed = datetime.strptime(dob_str, '%d-%m-%Y').strftime('%Y-%m-%d')
                                    except:
                                        try:
                                            dob_parsed = datetime.strptime(dob_str, '%d/%m/%y').strftime('%Y-%m-%d')
                                        except:
                                            dob_parsed = '2000-01-01'
                            
                            # Calculate expiry date
                            package_days = {
                                "1 Month - 8": 30, "3 Month - 24": 90, 
                                "6 Month - 48": 180, "12 Month - 96": 365,
                                "No Package": 0
                            }
                            days = package_days.get(str(row['class_plan']).strip(), 30)
                            expiry_date = start_date + timedelta(days=days)
                            
                            # Get total classes from plan
                            plan_str = str(row['class_plan']).strip() if row['class_plan'] else 'No Package'
                            if plan_str == 'nan' or not plan_str:
                                plan_str = 'No Package'
                            total_classes = int(plan_str.split(' - ')[1]) if ' - ' in plan_str else 0
                            
                            # Handle age conversion safely
                            age_val = row['age'] if row['age'] and str(row['age']) != 'nan' else 18
                            try:
                                age_int = int(float(str(age_val)))
                            except:
                                age_int = 18
                            
                            cursor.execute('''
                                INSERT INTO students 
                                (student_id, full_name, age, mobile, email, date_of_birth, sex, 
                                 instrument, class_plan, total_classes, start_date, expiry_date)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                student_id, 
                                str(row['full_name']).strip() if row['full_name'] else 'Unknown', 
                                age_int,
                                str(row['mobile']).strip() if row['mobile'] else '', 
                                str(row['email']).strip() if row['email'] else '', 
                                dob_parsed, 
                                str(row['sex']).strip() if row['sex'] else 'Male', 
                                str(row['instrument']).strip() if row['instrument'] else 'Piano', 
                                plan_str, total_classes,
                                start_date.strftime('%Y-%m-%d'), expiry_date.strftime('%Y-%m-%d')
                            ))
                            success_count += 1
                        except Exception as e:
                            error_count += 1
                            st.error(f"Error adding {row.get('full_name', 'Unknown')}: {str(e)}")
                    
                    conn.commit()
                    conn.close()
                    
                    if success_count > 0:
                        st.success(f"✅ Successfully added {success_count} students!")
                    if error_count > 0:
                        st.warning(f"⚠️ {error_count} students failed to upload")
                    
                    st.rerun()
            
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
    
    st.divider()
    
    st.subheader("⚠️ Important: Data Persistence")
    st.warning("""
    **Why students disappear after deployment:**
    - Streamlit Cloud resets files on each deployment
    - Only files in Git repository persist
    - New students added after deployment are lost unless committed to Git
    
    **Solution:**
    1. Export data regularly using buttons above
    2. For permanent storage, contact admin to commit database changes
    3. Consider upgrading to cloud database (PostgreSQL) for automatic persistence
    """)
    
    if st.button("🔄 Refresh Database Stats"):
        st.rerun()
    
    if st.button("← Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()

# Add this to your main app.py navigation
def add_backup_to_navigation():
    """Add backup option to sidebar"""
    return st.sidebar.selectbox("Select Page", [
        "Add Student", "View Students", "Process Payment", 
        "Due Alerts", "Payment Overview", "Database Backup"
    ])