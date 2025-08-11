import streamlit as st
from datetime import datetime, time
import sqlite3

def security_settings_module():
    """Security Settings Interface"""
    st.markdown("### 🔒 Security Settings")
    
    # Current security status
    st.markdown("#### 📊 Current Security Status")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Business hours status
        current_time = datetime.now().time()
        business_start = time(9, 0)
        business_end = time(20, 0)
        
        if business_start <= current_time <= business_end:
            st.success("✅ Within Business Hours (9 AM - 8 PM)")
        else:
            st.error("❌ Outside Business Hours")
        
        # Day status
        current_day = datetime.now().weekday()
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        if current_day != 6:  # Not Sunday
            st.success(f"✅ Business Day ({days[current_day]})")
        else:
            st.error("❌ Non-Business Day (Sunday)")
    
    with col2:
        # Session info
        if 'session_start' in st.session_state:
            session_duration = datetime.now() - st.session_state.session_start
            hours = int(session_duration.total_seconds() // 3600)
            minutes = int((session_duration.total_seconds() % 3600) // 60)
            
            if session_duration.total_seconds() < 14400:  # Less than 4 hours
                st.success(f"✅ Session Active ({hours}h {minutes}m)")
            else:
                st.error("❌ Session Expired (>4 hours)")
        else:
            st.info("ℹ️ No active session")
        
        # Device status
        if 'authorized_device' in st.session_state:
            st.success("✅ Authorized Device")
        else:
            st.warning("⚠️ Device Not Authorized")
    
    st.divider()
    
    # Security Settings
    st.markdown("#### ⚙️ Security Configuration")
    
    # Authorized devices management
    st.markdown("**Device Authorization:**")
    
    if st.button("🔓 Authorize This Device", use_container_width=True):
        st.session_state.authorized_device = True
        st.success("✅ Device authorized for future access")
        st.rerun()
    
    if st.button("🔒 Revoke Device Authorization", use_container_width=True):
        if 'authorized_device' in st.session_state:
            del st.session_state.authorized_device
        st.success("✅ Device authorization revoked")
        st.rerun()
    
    st.divider()
    
    # Security Rules
    st.markdown("#### 📋 Security Rules")
    st.info("""
    **Access Restrictions:**
    - ⏰ **Business Hours:** 9:00 AM to 8:00 PM only
    - 📅 **Business Days:** Monday to Saturday (Sunday blocked)
    - 🕐 **Session Timeout:** 4 hours maximum
    - 📱 **Device Authorization:** Required for each device
    - 🔐 **Login Required:** Username and password protection
    """)
    
    st.warning("""
    **Security Features:**
    - Automatic logout after 4 hours
    - No Sunday access
    - No late night/early morning access
    - Device fingerprinting for authorization
    """)
    
    if st.button("← Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()