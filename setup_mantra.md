# Mantra Fingerprint Scanner Setup Guide

## Current Status
✅ **Basic integration ready** - The system now supports Mantra fingerprint scanner with database storage.

## To Connect Your Physical Mantra Scanner:

### Step 1: Download Mantra SDK
1. Visit: https://www.mantratec.com/download/
2. Download "MFS100 SDK" for your operating system
3. Install the SDK and drivers

### Step 2: Install SDK Dependencies
```bash
# For Windows
pip install pywin32 comtypes

# For Linux/Mac
pip install pyusb libusb1
```

### Step 3: Update Scanner Code
Replace the simulation code in `mantra_simple.py` with actual Mantra SDK calls:

```python
# Replace simulation with actual SDK
from MFS100 import MFS100Device

def connect_scanner(self):
    self.device = MFS100Device()
    result = self.device.Init()
    if result == 0:
        self.is_connected = True
        return True, "Scanner connected"
    return False, "Connection failed"
```

## Current Features Working:
- ✅ Database storage for fingerprints
- ✅ Student enrollment interface
- ✅ Attendance marking system
- ✅ Scanner status monitoring
- ✅ Professional UI integration

## Next Steps:
1. Connect your Mantra scanner via USB
2. Install the official Mantra SDK
3. Replace simulation code with real SDK calls
4. Test fingerprint enrollment and scanning

The system is ready - just needs the physical scanner connection!