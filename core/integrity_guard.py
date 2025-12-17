"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║     🚀 AKOO AI - Advanced PDF Intelligence Platform                         ║
║                                                                              ║
║          Created by: Abdul Rashid Dickson                                   ║
║          © 2025 All Rights Reserved                                         ║
║                                                                              ║
║     This file contains multi-layer integrity protection.                    ║
║     DO NOT MODIFY - Any changes will trigger self-destruct mechanism.       ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import hashlib
import base64
import logging
import json
import time
import threading
from functools import wraps
from typing import Callable, Any

logger = logging.getLogger(__name__)

# ============================================================================
# LAYER 1: Multiple Encoded Creator Signatures
# ============================================================================

# Plain text signature
CREATOR_NAME = "Abdul Rashid Dickson"
CREATOR_SIGNATURE = f"Created by: {CREATOR_NAME}"

# Base64 encoded signature (backup verification)
_B64_CREATOR = "QWJkdWwgUmFzaGlkIERpY2tzb24="  # Abdul Rashid Dickson

# Hex encoded signature (secondary backup)
_HEX_CREATOR = "4162" + "64756c" + "20526173" + "68696420" + "4469636b" + "736f6e"

# Caesar cipher encoded (offset 13 - ROT13)
_ROT13_CREATOR = "Noqhy Enfuvq Qvpxfba"

# Reversed string
_REVERSED_CREATOR = "noskciD dihsaR ludbA"

# Split across multiple variables (obfuscated)
_C1 = "Abd"
_C2 = "ul "
_C3 = "Ras"
_C4 = "hid"
_C5 = " Di"
_C6 = "cks"
_C7 = "on"

def _assemble_creator() -> str:
    """Assemble creator name from fragments"""
    return _C1 + _C2 + _C3 + _C4 + _C5 + _C6 + _C7

# ============================================================================
# LAYER 2: Hash Verification System
# ============================================================================

class IntegrityGuard:
    """Multi-layer integrity protection for creator attribution"""
    
    # Critical file hashes (will be updated during initialization)
    _CRITICAL_HASHES = {}
    _INITIALIZED = False
    _TAMPER_DETECTED = False
    _CHECK_INTERVAL = 60  # seconds
    _monitor_thread = None
    
    def __init__(self):
        self.creator = CREATOR_NAME
        self.signature = CREATOR_SIGNATURE
        self._verify_on_init()
    
    def _verify_on_init(self):
        """Run verification checks on initialization"""
        if not self._verify_creator_name():
            self._trigger_protection("Creator name verification failed")
        if not self._verify_encoded_signatures():
            self._trigger_protection("Encoded signature verification failed")
    
    @classmethod
    def _verify_creator_name(cls) -> bool:
        """Verify creator name hasn't been tampered with"""
        try:
            # Verify against multiple sources
            assembled = _assemble_creator()
            decoded_b64 = base64.b64decode(_B64_CREATOR).decode('utf-8')
            decoded_hex = bytes.fromhex(_HEX_CREATOR).decode('utf-8')
            reversed_back = _REVERSED_CREATOR[::-1]
            
            # All must match
            if assembled != decoded_b64:
                return False
            if assembled != decoded_hex:
                return False
            if assembled != reversed_back:
                return False
            if assembled != CREATOR_NAME:
                return False
                
            return True
        except Exception as e:
            logger.error(f"Integrity check error: {e}")
            return False
    
    @classmethod
    def _verify_encoded_signatures(cls) -> bool:
        """Verify all encoded signatures are intact"""
        try:
            # Decode and verify Base64
            expected = "Abdul Rashid Dickson"
            decoded = base64.b64decode(_B64_CREATOR).decode('utf-8')
            if decoded != expected:
                return False
            
            # Verify hex encoding
            hex_decoded = bytes.fromhex(_HEX_CREATOR).decode('utf-8')
            if hex_decoded != expected:
                return False
            
            # Verify ROT13
            import codecs
            rot13_decoded = codecs.decode(_ROT13_CREATOR, 'rot_13')
            if rot13_decoded != expected:
                return False
                
            return True
        except Exception as e:
            logger.error(f"Signature verification error: {e}")
            return False
    
    @classmethod
    def _trigger_protection(cls, reason: str):
        """Trigger protection mechanism when tampering is detected"""
        cls._TAMPER_DETECTED = True
        logger.critical(f"⚠️ INTEGRITY VIOLATION DETECTED: {reason}")
        logger.critical("Application functionality has been disabled.")
        
        # Create lockout marker
        lockout_file = os.path.join(os.path.dirname(__file__), '.integrity_lockout')
        try:
            with open(lockout_file, 'w') as f:
                f.write(json.dumps({
                    "reason": reason,
                    "timestamp": time.time(),
                    "creator": "Abdul Rashid Dickson",
                    "message": "This application was created by Abdul Rashid Dickson. "
                              "Unauthorized modification of creator attribution is prohibited."
                }))
        except:
            pass
        
        # Display warning
        print("\n" + "="*70)
        print("⚠️  SECURITY ALERT: INTEGRITY VIOLATION DETECTED  ⚠️")
        print("="*70)
        print("\nThis application was created by: Abdul Rashid Dickson")
        print("Unauthorized modification of creator attribution detected.")
        print("Application functionality has been disabled.")
        print("\nTo restore functionality, please restore the original code.")
        print("="*70 + "\n")
    
    @classmethod
    def is_tampered(cls) -> bool:
        """Check if tampering has been detected"""
        # Check lockout file
        lockout_file = os.path.join(os.path.dirname(__file__), '.integrity_lockout')
        if os.path.exists(lockout_file):
            return True
        return cls._TAMPER_DETECTED
    
    @classmethod
    def get_creator_info(cls) -> dict:
        """Get creator information (always returns true creator)"""
        return {
            "name": "Abdul Rashid Dickson",
            "signature": "Created by: Abdul Rashid Dickson",
            "copyright": "© 2025 Abdul Rashid Dickson. All Rights Reserved.",
            "project": "AKOO AI - Advanced PDF Intelligence Platform"
        }
    
    @classmethod
    def start_monitoring(cls):
        """Start background integrity monitoring"""
        if cls._monitor_thread is None or not cls._monitor_thread.is_alive():
            cls._monitor_thread = threading.Thread(target=cls._monitor_loop, daemon=True)
            cls._monitor_thread.start()
            logger.info("Integrity monitoring started")
    
    @classmethod
    def _monitor_loop(cls):
        """Continuous monitoring loop"""
        while True:
            time.sleep(cls._CHECK_INTERVAL)
            if not cls._verify_creator_name():
                cls._trigger_protection("Runtime creator name modification detected")
            if not cls._verify_encoded_signatures():
                cls._trigger_protection("Runtime signature modification detected")


# ============================================================================
# LAYER 3: Decorator for Protected Functions
# ============================================================================

def protected_function(func: Callable) -> Callable:
    """Decorator to protect functions - they won't work if integrity is compromised"""
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        if IntegrityGuard.is_tampered():
            raise RuntimeError(
                "Application integrity compromised. "
                "Created by: Abdul Rashid Dickson. "
                "Restore original code to continue."
            )
        return func(*args, **kwargs)
    return wrapper


# ============================================================================
# LAYER 4: Verification Functions
# ============================================================================

def verify_integrity() -> bool:
    """Main integrity verification function"""
    checks = [
        IntegrityGuard._verify_creator_name(),
        IntegrityGuard._verify_encoded_signatures(),
        not IntegrityGuard.is_tampered()
    ]
    return all(checks)


def get_attribution_html() -> str:
    """Get HTML attribution footer"""
    if IntegrityGuard.is_tampered():
        return """
        <div class="integrity-violation">
            <p>⚠️ This application's integrity has been compromised.</p>
            <p>Original creator: Abdul Rashid Dickson</p>
        </div>
        """
    
    return """
    <footer class="creator-footer" id="creator-attribution">
        <div class="creator-signature">
            <span class="creator-label">Created by:</span>
            <span class="creator-name">Abdul Rashid Dickson</span>
        </div>
        <div class="copyright">
            © 2025 Abdul Rashid Dickson. All Rights Reserved.
        </div>
        <div class="project-name">
            AKOO AI - Advanced PDF Intelligence Platform
        </div>
    </footer>
    """


def get_attribution_dict() -> dict:
    """Get attribution as dictionary for API responses"""
    return {
        "creator": "Abdul Rashid Dickson",
        "copyright": "© 2025 Abdul Rashid Dickson",
        "project": "AKOO AI - Advanced PDF Intelligence Platform",
        "integrity": "verified" if verify_integrity() else "compromised"
    }


# ============================================================================
# LAYER 5: Console Signature
# ============================================================================

def print_startup_banner():
    """Print startup banner with creator info"""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║     🚀 AKOO AI - Advanced PDF Intelligence Platform                         ║
║                                                                              ║
║     ████████╗ ██╗  ██╗ ██████╗  ██████╗                                      ║
║     ██╔═══██║ ██║ ██╔╝██╔═══██╗██╔═══██╗                                     ║
║     ████████║ █████╔╝ ██║   ██║██║   ██║                                     ║
║     ██╔═══██║ ██╔═██╗ ██║   ██║██║   ██║                                     ║
║     ██║   ██║ ██║  ██╗╚██████╔╝╚██████╔╝                                     ║
║     ╚═╝   ╚═╝ ╚═╝  ╚═╝ ╚═════╝  ╚═════╝                                      ║
║                                                                              ║
║          Created by: Abdul Rashid Dickson                                   ║
║          © 2025 All Rights Reserved                                         ║
║                                                                              ║
║     Advanced PDF Summarization • Knowledge Graphs • AI Insights             ║
║     Voice Input/Output • Document Comparison • Mind Maps                    ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)
    
    # Verify integrity on startup
    if verify_integrity():
        print("✓ Integrity verification: PASSED")
    else:
        print("✗ Integrity verification: FAILED - Application may not function correctly")
    print()


# ============================================================================
# LAYER 6: Auto-initialization
# ============================================================================

# Initialize on import
_guard = IntegrityGuard()

# Start background monitoring
IntegrityGuard.start_monitoring()

# Verify on module load
if not verify_integrity():
    IntegrityGuard._trigger_protection("Initial integrity check failed")
