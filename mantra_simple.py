import sqlite3
import json
import time
from datetime import datetime

class MantraSimpleScanner:
    def __init__(self):
        self.is_connected = False
        self.enrolled_fingerprints = self.load_enrolled_fingerprints()
        self.device_info = "Mantra MFS100 Fingerprint Scanner"
    
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
            # Simulate connection - replace with actual Mantra SDK calls
            time.sleep(1)
            self.is_connected = True
            return True, "✅ Mantra scanner connected successfully"
        except Exception as e:
            return False, f"❌ Scanner connection error: {str(e)}"
    
    def disconnect_scanner(self):
        """Disconnect scanner"""
        self.is_connected = False
        return True, "Scanner disconnected"
    
    def enroll_fingerprint(self, student_id):
        """Enroll fingerprint for a student"""
        if not self.is_connected:
            return False, "Scanner not connected"
        
        try:
            # Simulate fingerprint capture - replace with actual Mantra SDK calls
            print(f"📱 Place finger on scanner for {student_id}...")
            time.sleep(3)  # Simulate capture time
            
            # Generate template (replace with actual template from scanner)
            template = f"MANTRA_TEMPLATE_{student_id}_{int(time.time())}"
            
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
            
            return True, f"✅ Fingerprint enrolled successfully for {student_id}"
            
        except Exception as e:
            return False, f"❌ Enrollment error: {str(e)}"
    
    def scan_fingerprint(self):
        """Scan and match fingerprint"""
        if not self.is_connected:
            return False, None, "Scanner not connected"
        
        try:
            print("📱 Place finger on scanner...")
            time.sleep(2)  # Simulate scan time
            
            # Simulate matching - replace with actual Mantra SDK calls
            if self.enrolled_fingerprints:
                # For demo, return first enrolled student
                student_id = list(self.enrolled_fingerprints.keys())[0]
                return True, student_id, f"✅ Fingerprint matched for {student_id}"
            else:
                return False, None, "❌ No enrolled fingerprints found"
            
        except Exception as e:
            return False, None, f"❌ Scan error: {str(e)}"
    
    def get_enrolled_count(self):
        """Get count of enrolled fingerprints"""
        return len(self.enrolled_fingerprints)
    
    def get_device_info(self):
        """Get scanner device information"""
        if self.is_connected:
            return f"🔗 {self.device_info} (Connected)"
        else:
            return f"🔌 {self.device_info} (Disconnected)"

# Global scanner instance
mantra_scanner = MantraSimpleScanner()