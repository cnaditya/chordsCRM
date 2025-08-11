import streamlit as st
import sqlite3
from datetime import datetime

def ip_management_module():
    """IP Management Interface"""
    st.markdown("### 🔒 IP Access Management")
    st.markdown("Manage authorized IP addresses that can access the CRM system.")
    
    # Get current user IP
    try:
        headers = st.context.headers if hasattr(st.context, 'headers') else {}
        current_ip = headers.get('X-Forwarded-For', '127.0.0.1')
        if ',' in current_ip:
            current_ip = current_ip.split(',')[0].strip()
    except:
        current_ip = "Unknown"
    
    st.info(f"🌐 Your current IP address: **{current_ip}**")
    
    # Load current allowed IPs
    conn = sqlite3.connect('chords_crm.db')
    cursor = conn.cursor()
    cursor.execute('SELECT ip_address, description, added_date FROM allowed_ips ORDER BY added_date DESC')
    allowed_ips = cursor.fetchall()
    conn.close()
    
    # Display current allowed IPs
    st.markdown("#### 📋 Currently Allowed IP Addresses")
    
    if allowed_ips:
        for ip, desc, date_added in allowed_ips:
            col1, col2, col3, col4 = st.columns([2, 3, 2, 1])
            
            with col1:
                st.code(ip)
            with col2:
                st.write(desc)
            with col3:
                st.write(date_added)
            with col4:
                if st.button("🗑️", key=f"del_{ip}", help="Remove IP"):
                    if remove_allowed_ip(ip):
                        st.success(f"Removed {ip}")
                        st.rerun()
                    else:
                        st.error("Failed to remove IP")
    else:
        st.warning("No IP addresses configured")
    
    st.divider()
    
    # Add new IP section
    st.markdown("#### ➕ Add New Authorized IP")
    
    col1, col2 = st.columns(2)
    
    with col1:
        new_ip = st.text_input("🌐 IP Address", placeholder="e.g., 192.168.1.100 or 203.123.45.67")
        
        # Quick add buttons
        st.markdown("**Quick Add:**")
        if st.button("➕ Add Current IP", use_container_width=True):
            if current_ip != "Unknown":
                if add_allowed_ip(current_ip, "Added from current session"):
                    st.success(f"Added current IP: {current_ip}")
                    st.rerun()
                else:
                    st.error("Failed to add IP")
            else:
                st.error("Cannot detect current IP")
    
    with col2:
        description = st.text_input("📝 Description", placeholder="e.g., Home WiFi, Office Network")
        
        # IP range helper
        st.markdown("**Common Patterns:**")
        st.code("192.168.0.    # Local network range")
        st.code("203.123.45.67 # Specific IP")
    
    if st.button("✅ Add IP Address", type="primary", use_container_width=True):
        if new_ip and description:
            if add_allowed_ip(new_ip, description):
                st.success(f"✅ Added IP: {new_ip}")
                st.rerun()
            else:
                st.error("❌ Failed to add IP (might already exist)")
        else:
            st.error("⚠️ Please fill in both IP address and description")
    
    st.divider()
    
    # Security info
    st.markdown("#### 🛡️ Security Information")
    st.info("""
    **How IP Restriction Works:**
    - Only IP addresses in the list above can access this CRM
    - IP ranges (like 192.168.0.) allow entire network access
    - Specific IPs (like 203.123.45.67) allow only that exact address
    - Changes take effect immediately
    """)
    
    st.warning("""
    **⚠️ Important:**
    - Don't remove your current IP or you'll lose access
    - Always test new IPs before removing old ones
    - Keep at least one working IP in the list
    """)

def add_allowed_ip(ip_address, description):
    """Add new allowed IP to database"""
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
    """Remove allowed IP from database"""
    try:
        conn = sqlite3.connect('chords_crm.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM allowed_ips WHERE ip_address = ?', (ip_address,))
        conn.commit()
        conn.close()
        return True
    except:
        return False