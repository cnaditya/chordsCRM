# Simple working version of student list
def student_list_module_simple():
    display_header("Student Management", "Search, Edit & Manage Student Records")
    
    students = get_all_students()
    if not students:
        st.info("No students registered yet.")
        if st.button("← Back to Dashboard"):
            st.session_state.page = "dashboard"
            st.rerun()
        return
    
    df = pd.DataFrame(students, columns=[
        'ID', 'Student ID', 'Full Name', 'Age', 'Mobile', 'Instrument', 'Class Plan', 
        'Total Classes', 'Start Date', 'Expiry Date', 'Status', 'Classes Completed', 
        'Extra Classes', 'First Class Date', 'Email', 'Date of Birth', 'Sex'
    ])
    
    # Search section
    st.markdown("### 🔍 Find Student")
    col1, col2 = st.columns(2)
    
    with col1:
        search_term = st.text_input("🔍 Search by Name or ID", placeholder="Enter student name or ID")
    
    with col2:
        if st.button("📊 Show All Students", use_container_width=True):
            search_term = "SHOW_ALL"
    
    # Apply search
    if search_term:
        if search_term == "SHOW_ALL":
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
                    st.text(f"Age: {student['Age']}")
                    st.text(f"Mobile: {student['Mobile']}")
                
                with col2:
                    st.markdown("**🎵 Course Info**")
                    st.text(f"Instrument: {student['Instrument']}")
                    st.text(f"Package: {student['Class Plan']}")
                    st.text(f"Classes: {student['Classes Completed']}/{student['Total Classes']}")
                
                with col3:
                    st.markdown("**📅 Dates**")
                    start_date = str(student['Start Date']).split(' ')[0]
                    st.text(f"Start: {pd.to_datetime(start_date).strftime('%d-%m-%Y')}")
                    if student['Class Plan'] != 'No Package':
                        expiry_date = str(student['Expiry Date']).split(' ')[0]
                        st.text(f"Expiry: {pd.to_datetime(expiry_date).strftime('%d-%m-%Y')}")
                    else:
                        st.text("Expiry: No Package")
                
                st.divider()
                
                # Edit form
                st.markdown("**✏️ Edit Student**")
                
                ecol1, ecol2 = st.columns(2)
                
                with ecol1:
                    new_name = st.text_input("Full Name", value=student['Full Name'], key=f"name_{student['Student ID']}")
                    new_age = st.number_input("Age", value=int(student['Age']), min_value=1, max_value=100, key=f"age_{student['Student ID']}")
                    new_mobile = st.text_input("Mobile", value=student['Mobile'], key=f"mobile_{student['Student ID']}")
                
                with ecol2:
                    new_instrument = st.selectbox("Instrument", 
                                                ["Keyboard", "Piano", "Guitar", "Drums", "Violin", "Flute", "Carnatic Vocals", "Hindustani Vocals", "Western Vocals"],
                                                index=["Keyboard", "Piano", "Guitar", "Drums", "Violin", "Flute", "Carnatic Vocals", "Hindustani Vocals", "Western Vocals"].index(student['Instrument']),
                                                key=f"inst_{student['Student ID']}")
                    
                    new_package = st.selectbox("Package", 
                                             ["No Package", "1 Month - 8", "3 Month - 24", "6 Month - 48", "12 Month - 96"],
                                             index=["No Package", "1 Month - 8", "3 Month - 24", "6 Month - 48", "12 Month - 96"].index(student['Class Plan']),
                                             key=f"pkg_{student['Student ID']}")
                    
                    new_start_date = st.date_input("Start Date", 
                                                  value=pd.to_datetime(start_date).date(),
                                                  key=f"start_{student['Student ID']}")
                
                # Save button
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
    
    else:
        st.info("🔍 Enter search criteria to view student records")
    
    if st.button("← Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()