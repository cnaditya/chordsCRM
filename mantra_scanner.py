import sqlite3
import json
from datetime import datetime

class MantraScanner:
    def __init__(self):
        self.is_connected = False
        self.device = None
        self.enrolled_fingerprints = self.load_enrolled_fingerprints()
    
    def load_enrolled_fingerprints(self):
        """Load enrolled fingerprints from database"""
        try:
            conn = sqlite3.connect('chords_crm.db')
            cursor = conn.cursor()
            
            # Create fingerprints table if not exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS fingerprints (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT UNIQUE,
                    fingerprint_template TEXT,
                    enrollment_date TEXT
                )
            ''')
            
            cursor.execute('SELECT student_id, fingerprint_template FROM fingerprints')
            fingerprints = dict(cursor.fetchall())
            conn.close()
            return fingerprints
        except:
            return {}
    
    def connect_scanner(self):
        """Connect to Mantra fingerprint scanner"""
        try:
            # Import Mantra SDK (you need to install this)
            # pip install mantra-mfs100
            from mantra import MFS100
            
            self.device = MFS100()
            result = self.device.Init()
            
            if result == 0:  # Success
                self.is_connected = True
                return True, "Mantra scanner connected successfully"
            else:
                return False, f"Failed to connect scanner. Error code: {result}"
                
        except ImportError:
            return False, "Mantra SDK not installed. Please install: pip install mantra-mfs100"
        except Exception as e:
            return False, f"Scanner connection error: {str(e)}"
    
    def disconnect_scanner(self):
        """Disconnect scanner"""
        try:
            if self.device:
                self.device.Uninit()
            self.is_connected = False
            return True, "Scanner disconnected"
        except:
            return False, "Error disconnecting scanner"
    
    def enroll_fingerprint(self, student_id):
        """Enroll fingerprint for a student"""
        if not self.is_connected:
            return False, "Scanner not connected"
        
        try:
            # Capture fingerprint template
            result, template = self.device.CaptureFinger()
            
            if result == 0 and template:
                # Save to database
                conn = sqlite3.connect('chords_crm.db')
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO fingerprints (student_id, fingerprint_template, enrollment_date)
                    VALUES (?, ?, ?)
                ''', (student_id, template, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                conn.commit()
                conn.close()
                
                # Update local cache
                self.enrolled_fingerprints[student_id] = template
                
                return True, f"Fingerprint enrolled successfully for {student_id}"
            else:
                return False, "Failed to capture fingerprint. Please try again."
                
        except Exception as e:
            return False, f"Enrollment error: {str(e)}"
    
    def scan_fingerprint(self):
        """Scan and match fingerprint"""
        if not self.is_connected:
            return False, None, "Scanner not connected"
        
        try:
            # Capture fingerprint
            result, captured_template = self.device.CaptureFinger()
            
            if result != 0 or not captured_template:
                return False, None, "Failed to capture fingerprint"
            
            # Match against enrolled fingerprints
            for student_id, enrolled_template in self.enrolled_fingerprints.items():
                match_result = self.device.MatchFinger(captured_template, enrolled_template)
                
                if match_result >= 70:  # Match threshold (adjust as needed)
                    return True, student_id, f"Fingerprint matched for {student_id}"
            
            return False, None, "Fingerprint not recognized"
            
        except Exception as e:
            return False, None, f"Scan error: {str(e)}"
    
    def get_enrolled_count(self):
        """Get count of enrolled fingerprints"""
        return len(self.enrolled_fingerprints)
    
    def get_device_info(self):
        """Get scanner device information"""
        if not self.is_connected:
            return "Scanner not connected"
        
        try:
            info = self.device.GetDeviceInfo()
            return f"Device: {info.get('model', 'Unknown')} - Serial: {info.get('serial', 'Unknown')}"
        except:
            return "Mantra Fingerprint Scanner"

# Global scanner instance
mantra_scanner = MantraScanner()