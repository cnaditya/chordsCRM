import requests

# Test exactly as shown in your Excel sheet
url = "https://www.fast2sms.com/dev/whatsapp?authorization=6TDScuetHNniG5F92kswhvrLJx4IAVRjpoZUb1Y83CzBl0WEd7RLDaifTQwBqekSC2vnMz583p4lKsdX&message_id=3004&numbers=917702031818&variables_values=Test|Package|01-01-2025"

response = requests.get(url)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")