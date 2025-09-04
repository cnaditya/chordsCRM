with open('app.py', 'r') as f:
    content = f.read()

# Find and replace the debug section completely
old_section = '''    # Debug section
    st.markdown("---")
    st.markdown("### 🔧 Debug WhatsApp")
    
    if st.button("🧪 Test WhatsApp API", key="test_api_unique"):
        from sms_email import test_fast2sms
        status, response = test_fast2sms()
        st.write(f"Status: {status}")
        st.write(f"Response: {response}")
    
    if st.button("📱 Test WhatsApp Receipt", key="test_receipt_unique"):
            success, message = send_whatsapp_payment_receipt(
                "7702031818", "Test Student", 1000, "CMA00001", 
                "1 Month - 8", datetime.now().strftime('%Y-%m-%d'), "Next Due: 01-10-2024"
            )
            if success:
                st.success(f"✅ Test successful: {message}")
            else:
                st.error(f"❌ Test failed: {message}")'''

new_section = '''    # Debug section
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
            st.error(f"❌ Test failed: {message}")'''

content = content.replace(old_section, new_section)

with open('app.py', 'w') as f:
    f.write(content)

print("Force fixed buttons")