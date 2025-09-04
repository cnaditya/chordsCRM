import re

with open('app.py', 'r') as f:
    content = f.read()

# Add unique keys to buttons
content = content.replace(
    'if st.button("🧪 Test WhatsApp API"):',
    'if st.button("🧪 Test WhatsApp API", key="test_api_unique"):'
)

content = content.replace(
    'if st.button("📱 Test WhatsApp Receipt"):',
    'if st.button("📱 Test WhatsApp Receipt", key="test_receipt_unique"):'
)

with open('app.py', 'w') as f:
    f.write(content)

print("Fixed button keys")