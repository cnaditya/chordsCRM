#!/usr/bin/env python3
"""
Installation script for Mantra fingerprint scanner integration
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages for Mantra scanner"""
    
    print("🔧 Installing Mantra Fingerprint Scanner Requirements...")
    
    # Required packages
    packages = [
        "pywin32",  # For Windows COM interface
        "comtypes", # For COM type libraries
    ]
    
    for package in packages:
        try:
            print(f"📦 Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} installed successfully")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")
    
    print("\n📋 Manual Setup Required:")
    print("1. Download Mantra MFS100 SDK from: https://www.mantratec.com/")
    print("2. Install the SDK and drivers")
    print("3. Register the COM components")
    print("4. Connect your Mantra fingerprint scanner")
    
    print("\n🔧 Alternative: Create mantra.py wrapper")
    create_mantra_wrapper()

def create_mantra_wrapper():
    """Create a wrapper for Mantra SDK"""
    
    wrapper_code = '''
import win32com.client
import pythoncom

class MFS100:
    def __init__(self):
        try:
            pythoncom.CoInitialize()
            self.device = win32com.client.Dispatch("MFS100.MFS100X")
        except Exception as e:
            raise Exception(f"Failed to initialize Mantra device: {e}")
    
    def Init(self):
        """Initialize the device"""
        try:
            return self.device.Init()
        except:
            return -1
    
    def Uninit(self):
        """Uninitialize the device"""
        try:
            return self.device.Uninit()
        except:
            return -1
    
    def CaptureFinger(self):
        """Capture fingerprint and return template"""
        try:
            result = self.device.CaptureFinger()
            if result == 0:
                template = self.device.GetTemplate()
                return 0, template
            return result, None
        except:
            return -1, None
    
    def MatchFinger(self, template1, template2):
        """Match two fingerprint templates"""
        try:
            return self.device.MatchFinger(template1, template2)
        except:
            return 0
    
    def GetDeviceInfo(self):
        """Get device information"""
        try:
            return {
                "model": "MFS100",
                "serial": self.device.GetDeviceInfo()
            }
        except:
            return {"model": "Unknown", "serial": "Unknown"}
'''
    
    try:
        with open("/Users/aaditya/chords_crm/mantra.py", "w") as f:
            f.write(wrapper_code)
        print("✅ Created mantra.py wrapper")
    except Exception as e:
        print(f"❌ Failed to create wrapper: {e}")

if __name__ == "__main__":
    install_requirements()