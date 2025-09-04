#!/usr/bin/env python3
"""Quick fix for button visibility issues"""

import re

# Read the file
with open('app.py', 'r') as f:
    content = f.read()

# Fix the debug section - remove columns
old_debug = '''    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧪 Test WhatsApp API"):
            from sms_email import test_fast2sms
            status, response = test_fast2sms()
            st.write(f"Status: {status}")
            st.write(f"Response: {response}")
    
    with col2:
        if st.button("📱 Test WhatsApp Receipt"):'''

new_debug = '''    if st.button("🧪 Test WhatsApp API"):
        from sms_email import test_fast2sms
        status, response = test_fast2sms()
        st.write(f"Status: {status}")
        st.write(f"Response: {response}")
    
    if st.button("📱 Test WhatsApp Receipt"):'''

# Replace
content = content.replace(old_debug, new_debug)

# Write back
with open('app.py', 'w') as f:
    f.write(content)

print("Fixed button visibility issue")