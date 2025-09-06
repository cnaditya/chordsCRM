import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

def create_backup_page():
    """Create a backup/export page for database"""
    st.header("🔄 Database Backup & Export")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Current Database Stats")
        conn = sqlite3.connect('chords_crm.db')
        
        # Get counts
        students_count = pd.read_sql_query("SELECT COUNT(*) as count FROM students_enhanced WHERE is_active = 1", conn).iloc[0]['count']
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
            df = pd.read_sql_query("SELECT * FROM students_enhanced WHERE is_active = 1", conn)
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

# Add this to your main app.py navigation
def add_backup_to_navigation():
    """Add backup option to sidebar"""
    return st.sidebar.selectbox("Select Page", [
        "Add Student", "View Students", "Process Payment", 
        "Due Alerts", "Payment Overview", "Database Backup"
    ])