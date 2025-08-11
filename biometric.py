import time
import random

class BiometricScanner:
    def __init__(self):
        self.is_connected = False
        self.enrolled_fingerprints = {}  # student_id: fingerprint_data
    
    def connect_scanner(self):
        """Simulate scanner connection"""
        time.sleep(1)
        self.is_connected = True
        return True, "Scanner connected successfully"
    
    def disconnect_scanner(self):
        """Disconnect scanner"""
        self.is_connected = False
        return True, "Scanner disconnected"
    
    def enroll_fingerprint(self, student_id):
        """Enroll fingerprint for a student"""
        if not self.is_connected:
            return False, "Scanner not connected"
        
        # Simulate fingerprint enrollment
        time.sleep(2)
        fingerprint_data = f"FP_{student_id}_{random.randint(1000, 9999)}"
        self.enrolled_fingerprints[student_id] = fingerprint_data
        return True, f"Fingerprint enrolled for {student_id}"
    
    def scan_fingerprint(self):
        """Scan and match fingerprint"""
        if not self.is_connected:
            return False, None, "Scanner not connected"
        
        # Simulate fingerprint scanning
        time.sleep(1)
        
        # Simulate successful match (random for demo)
        if self.enrolled_fingerprints and random.choice([True, False]):
            student_id = random.choice(list(self.enrolled_fingerprints.keys()))
            return True, student_id, "Fingerprint matched"
        else:
            return False, None, "Fingerprint not recognized"
    
    def get_enrolled_count(self):
        """Get count of enrolled fingerprints"""
        return len(self.enrolled_fingerprints)

# Global scanner instance
scanner = BiometricScanner()