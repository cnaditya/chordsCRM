def send_whatsapp_reminder(mobile, student_name, plan, expiry_date, include_qr=True):
    """Send WhatsApp reminder using Fast2SMS template 4986 - FIXED VERSION"""
    
    print(f"FUNCTION CALLED: send_whatsapp_reminder for {student_name} at {mobile}")
    
    # Clean and format mobile number for international support
    mobile = str(mobile).replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    
    # Add country code if not present
    if mobile.startswith("+"):
        mobile = mobile[1:]
    elif mobile.startswith("91") and len(mobile) == 12:
        pass
    elif len(mobile) == 10 and mobile.isdigit():
        mobile = "91" + mobile
    elif not mobile.isdigit():
        return False, f"Invalid mobile number format: {mobile}"
    
    # Validate final format
    if len(mobile) < 10 or len(mobile) > 15 or not mobile.isdigit():
        return False, f"Invalid mobile number: {mobile}. Must be 10-15 digits with country code."
    
    url = "https://www.fast2sms.com/dev/whatsapp"
    
    # Clean and format date to dd-mm-yyyy
    if " 00:00:00" in str(expiry_date):
        expiry_date = str(expiry_date).replace(" 00:00:00", "")
    
    # Convert to dd-mm-yyyy format
    try:
        from datetime import datetime
        date_obj = datetime.strptime(str(expiry_date), '%Y-%m-%d')
        expiry_date_formatted = date_obj.strftime('%d-%m-%Y')
    except:
        expiry_date_formatted = str(expiry_date)
    
    # Template 4986: API key in query params as per Fast2SMS format
    variables = f"{student_name}|{plan}|{expiry_date_formatted}"
    
    params = {
        "authorization": "6TDScuetHNniG5F92kswhvrLJx4IAVRjpoZUb1Y83CzBl0WEd7RLDaifTQwBqekSC2vnMz583p4lKsdX",
        "message_id": "4986",
        "numbers": mobile,
        "variables_values": variables
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        # Debug logging
        print(f"DEBUG 4986: URL: {url}")
        print(f"DEBUG 4986: Full URL: {response.url}")
        print(f"DEBUG 4986: Params: {params}")
        print(f"DEBUG 4986: Status: {response.status_code}")
        print(f"DEBUG 4986: Response: {response.text}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"DEBUG 4986: JSON Result: {result}")
                
                if result.get('return') == True:
                    return True, "WhatsApp reminder with payment options sent successfully"
                else:
                    error_msg = result.get('message', result.get('error', f'Unknown error - Raw JSON: {result}'))
                    return False, f"Template 4986 Error: {error_msg}"
            except:
                return False, f"Invalid JSON response: {response.text}"
        else:
            return False, f"HTTP {response.status_code}: {response.text}"
    except Exception as e:
        print(f"DEBUG 4986: Exception occurred: {str(e)}")
        return False, f"Network Error: {str(e)}"