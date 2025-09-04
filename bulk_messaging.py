"""
Bulk Messaging Module for Chords CRM
Handles Fast2SMS WhatsApp bulk messaging with templates
"""

import requests
from datetime import datetime

FAST2SMS_API_KEY = "6TDScuetHNniG5F92kswhvrLJx4IAVRjpoZUb1Y83CzBl0WEd7RLDaifTQwBqekSC2vnMz583p4lKsdX"

# BULK MESSAGING TEMPLATES
BULK_TEMPLATES = {
    # GENERAL TEMPLATES (All Students)
    "general_holiday": {"id": "5001", "vars": "student_name|date|reason|resume_date"},
    "festival_holiday": {"id": "5002", "vars": "student_name|festival_name|date|resume_date"},
    "emergency_closure": {"id": "5003", "vars": "student_name|date|emergency_reason"},
    "weather_closure": {"id": "5007", "vars": "student_name|weather_condition|date|resume_date"},
    "transport_strike": {"id": "5008", "vars": "student_name|strike_reason|date|resume_date"},
    
    # INSTRUMENT-SPECIFIC TEMPLATES
    "piano_sick_leave": {"id": "5011", "vars": "student_name|date|instructor_name"},
    "guitar_sick_leave": {"id": "5012", "vars": "student_name|date|instructor_name"},
    "drums_sick_leave": {"id": "5013", "vars": "student_name|date|instructor_name"},
    "violin_sick_leave": {"id": "5014", "vars": "student_name|date|instructor_name"},
    
    "piano_personal_leave": {"id": "5015", "vars": "student_name|date|instructor_name"},
    "guitar_personal_leave": {"id": "5016", "vars": "student_name|date|instructor_name"},
    "drums_personal_leave": {"id": "5017", "vars": "student_name|date|instructor_name"},
    "violin_personal_leave": {"id": "5018", "vars": "student_name|date|instructor_name"},
    
    "piano_emergency": {"id": "5019", "vars": "student_name|date|instructor_name"},
    "guitar_emergency": {"id": "5020", "vars": "student_name|date|instructor_name"},
    "drums_emergency": {"id": "5021", "vars": "student_name|date|instructor_name"},
    "violin_emergency": {"id": "5022", "vars": "student_name|date|instructor_name"}
}

def send_bulk_whatsapp_message(mobile_numbers, template_key, **template_vars):
    """Send bulk WhatsApp messages using Fast2SMS templates"""
    
    if template_key not in BULK_TEMPLATES:
        return False, f"Template '{template_key}' not found"
    
    template = BULK_TEMPLATES[template_key]
    
    # Clean and format mobile numbers
    cleaned_numbers = []
    for mobile in mobile_numbers:
        mobile = str(mobile).replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        
        if mobile.startswith("+"):
            mobile = mobile[1:]
        elif mobile.startswith("91") and len(mobile) == 12:
            pass
        elif len(mobile) == 10 and mobile.isdigit():
            mobile = "91" + mobile
        
        if len(mobile) >= 10 and len(mobile) <= 15 and mobile.isdigit():
            cleaned_numbers.append(mobile)
    
    if not cleaned_numbers:
        return False, "No valid mobile numbers found"
    
    # Join numbers with comma for bulk sending
    numbers_string = ",".join(cleaned_numbers)
    
    # Build variables string based on template requirements
    var_names = template["vars"].split("|")
    variables = "|".join([str(template_vars.get(var, "")) for var in var_names])
    
    url = "https://www.fast2sms.com/dev/whatsapp"
    
    params = {
        "authorization": FAST2SMS_API_KEY,
        "message_id": template["id"],
        "numbers": numbers_string,
        "variables_values": variables,
        "sender_id": "CHORDS"
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            try:
                result = response.json()
                if result.get('return') == True:
                    return True, f"Bulk message sent to {len(cleaned_numbers)} students successfully"
                else:
                    error_msg = result.get('message', result.get('error', 'Unknown API error'))
                    return False, f"API Error: {error_msg}"
            except:
                return False, f"Invalid JSON response: {response.text}"
        else:
            return False, f"HTTP {response.status_code}: {response.text}"
    except Exception as e:
        return False, f"Network Error: {str(e)}"

def get_template_preview(template_key, **sample_vars):
    """Get preview of template with sample data"""
    
    template_previews = {
        "general_holiday": "Hi {student_name}, Chords Music Academy will be closed on {date} due to {reason}. All classes are cancelled. Regular classes will resume from {resume_date}. For queries: 7981585309 - Team Chords",
        "festival_holiday": "🎉 Hi {student_name}, Chords Music Academy wishes you Happy {festival_name}! Academy closed on {date}. Classes resume {resume_date}. Enjoy the celebrations! 🎶 - Team Chords",
        "emergency_closure": "⚠️ URGENT: Hi {student_name}, Chords Music Academy is closed today ({date}) due to {emergency_reason}. We'll update you about next class. Stay safe! - Team Chords",
        "weather_closure": "🌧️ Hi {student_name}, Due to heavy {weather_condition}, Chords Music Academy is closed today ({date}) for safety. Classes will resume {resume_date}. Stay safe! - Team Chords",
        "transport_strike": "Hi {student_name}, Due to {strike_reason} on {date}, Chords Music Academy classes are cancelled for student safety. Normal classes from {resume_date}. - Team Chords",
        
        "piano_sick_leave": "Hi {student_name}, Your Piano classes are cancelled today ({date}) as {instructor_name} sir is unwell. Makeup class will be scheduled soon. Get well soon sir! 🎹 - Team Chords",
        "guitar_sick_leave": "Hi {student_name}, Your Guitar classes are cancelled today ({date}) as {instructor_name} sir is unwell. Makeup class will be scheduled soon. Get well soon sir! 🎸 - Team Chords",
        "drums_sick_leave": "Hi {student_name}, Your Drums classes are cancelled today ({date}) as {instructor_name} sir is unwell. Makeup class will be scheduled soon. Get well soon sir! 🥁 - Team Chords",
        "violin_sick_leave": "Hi {student_name}, Your Violin classes are cancelled today ({date}) as {instructor_name} sir is unwell. Makeup class will be scheduled soon. Get well soon sir! 🎻 - Team Chords",
        
        "piano_personal_leave": "Hi {student_name}, Piano classes cancelled on {date} due to {instructor_name} sir's personal work. Alternative arrangement/makeup class will be informed. Thanks! 🎹 - Team Chords",
        "guitar_personal_leave": "Hi {student_name}, Guitar classes cancelled on {date} due to {instructor_name} sir's personal work. Alternative arrangement/makeup class will be informed. Thanks! 🎸 - Team Chords",
        "drums_personal_leave": "Hi {student_name}, Drums classes cancelled on {date} due to {instructor_name} sir's personal work. Alternative arrangement/makeup class will be informed. Thanks! 🥁 - Team Chords",
        "violin_personal_leave": "Hi {student_name}, Violin classes cancelled on {date} due to {instructor_name} sir's personal work. Alternative arrangement/makeup class will be informed. Thanks! 🎻 - Team Chords",
        
        "piano_emergency": "Hi {student_name}, Piano classes cancelled today ({date}) due to {instructor_name} sir's emergency. We'll reschedule your class. Sorry for inconvenience! 🎹 - Team Chords",
        "guitar_emergency": "Hi {student_name}, Guitar classes cancelled today ({date}) due to {instructor_name} sir's emergency. We'll reschedule your class. Sorry for inconvenience! 🎸 - Team Chords",
        "drums_emergency": "Hi {student_name}, Drums classes cancelled today ({date}) due to {instructor_name} sir's emergency. We'll reschedule your class. Sorry for inconvenience! 🥁 - Team Chords",
        "violin_emergency": "Hi {student_name}, Violin classes cancelled today ({date}) due to {instructor_name} sir's emergency. We'll reschedule your class. Sorry for inconvenience! 🎻 - Team Chords"
    }
    
    if template_key in template_previews:
        return template_previews[template_key].format(**sample_vars)
    return "Template preview not available"

def get_template_info():
    """Get information about all available templates"""
    return {
        "General Templates": {
            "general_holiday": "General Holiday Announcement",
            "festival_holiday": "Festival Holiday Wishes",
            "emergency_closure": "Emergency Academy Closure",
            "weather_closure": "Weather-related Closure",
            "transport_strike": "Transport Strike Closure"
        },
        "Instrument-Specific Templates": {
            "piano_sick_leave": "Piano Instructor Sick Leave",
            "guitar_sick_leave": "Guitar Instructor Sick Leave", 
            "drums_sick_leave": "Drums Instructor Sick Leave",
            "violin_sick_leave": "Violin Instructor Sick Leave",
            "piano_personal_leave": "Piano Instructor Personal Leave",
            "guitar_personal_leave": "Guitar Instructor Personal Leave",
            "drums_personal_leave": "Drums Instructor Personal Leave", 
            "violin_personal_leave": "Violin Instructor Personal Leave",
            "piano_emergency": "Piano Instructor Emergency",
            "guitar_emergency": "Guitar Instructor Emergency",
            "drums_emergency": "Drums Instructor Emergency",
            "violin_emergency": "Violin Instructor Emergency"
        }
    }