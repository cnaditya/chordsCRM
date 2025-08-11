# 🔒 Security Setup Guide

## IP Restriction Configuration

Your CRM now has IP-based access control to prevent outside access.

### Step 1: Find Your Office IP Address
```bash
# Visit this website from your office computer:
https://whatismyipaddress.com/

# Or use command line:
curl ifconfig.me
```

### Step 2: Update Allowed IPs
Edit `app.py` and replace `YOUR_OFFICE_IP_HERE` with your actual office IP:

```python
ALLOWED_IPS = [
    "192.168.0.",           # Local network range
    "203.123.45.67",        # Replace with your office public IP
    "127.0.0.1",            # Localhost for testing
]
```

### Step 3: Test Access
- ✅ **From Office**: Should work normally
- ❌ **From Home/Outside**: Will show "Access Denied"

## Additional Security Options

### Option 1: Local Network Only
Deploy on office computer and access via local IP:
```bash
streamlit run app.py --server.address 0.0.0.0
# Access via: http://192.168.0.X:8501
```

### Option 2: VPN Access
- Setup office VPN
- Receptionist connects to VPN from home
- Then accesses the web app

### Option 3: Time-based Access
Add working hours restriction:
```python
# Only allow access during business hours
import datetime
current_hour = datetime.datetime.now().hour
if not (9 <= current_hour <= 18):  # 9 AM to 6 PM
    st.error("System available only during business hours")
```

## Recommended Setup:
1. **IP Restriction** ✅ (Already added)
2. **Strong Password** (Change from admin/admin1)
3. **Local Network Deployment** (Most secure)

Your receptionist can only access from office, not from home! 🔒