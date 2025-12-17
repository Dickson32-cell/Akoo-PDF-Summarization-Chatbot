"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║     🚀 AKOO AI - Advanced PDF Intelligence Platform                         ║
║                                                                              ║
║          Created by: Abdul Rashid Dickson                                   ║
║          © 2025 All Rights Reserved                                         ║
║                                                                              ║
║     Watermarking module for creator attribution protection.                  ║
║     Embeds invisible creator signatures in all generated content.            ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import hashlib
import base64
import json
import time
from typing import Dict, Any, Optional

# Creator watermark constants - Abdul Rashid Dickson
_WATERMARK_CREATOR = "Abdul Rashid Dickson"
_WATERMARK_B64 = "QWJkdWwgUmFzaGlkIERpY2tzb24="
_WATERMARK_SIGNATURE = "AKOO-ARD-2025"


class Watermark:
    """Invisible watermarking for creator attribution protection"""
    
    # Zero-width characters for invisible text embedding
    ZERO_WIDTH_SPACE = '\u200b'  # U+200B
    ZERO_WIDTH_NON_JOINER = '\u200c'  # U+200C
    ZERO_WIDTH_JOINER = '\u200d'  # U+200D
    
    @classmethod
    def _text_to_binary(cls, text: str) -> str:
        """Convert text to binary string"""
        return ''.join(format(ord(c), '08b') for c in text)
    
    @classmethod
    def _binary_to_zero_width(cls, binary: str) -> str:
        """Convert binary to zero-width characters"""
        result = ""
        for bit in binary:
            if bit == '0':
                result += cls.ZERO_WIDTH_SPACE
            else:
                result += cls.ZERO_WIDTH_NON_JOINER
        return result
    
    @classmethod
    def _zero_width_to_binary(cls, zero_width: str) -> str:
        """Convert zero-width characters back to binary"""
        binary = ""
        for char in zero_width:
            if char == cls.ZERO_WIDTH_SPACE:
                binary += '0'
            elif char == cls.ZERO_WIDTH_NON_JOINER:
                binary += '1'
        return binary
    
    @classmethod
    def _binary_to_text(cls, binary: str) -> str:
        """Convert binary string back to text"""
        chars = [binary[i:i+8] for i in range(0, len(binary), 8)]
        return ''.join(chr(int(char, 2)) for char in chars if len(char) == 8)
    
    @classmethod
    def create_watermark(cls) -> str:
        """Create invisible watermark string"""
        watermark_data = f"ARD:{_WATERMARK_CREATOR}:{int(time.time())}"
        binary = cls._text_to_binary(watermark_data)
        return cls._binary_to_zero_width(binary)
    
    @classmethod
    def embed_watermark(cls, text: str) -> str:
        """Embed invisible creator watermark in text"""
        if not text:
            return text
        
        watermark = cls.create_watermark()
        
        # Insert watermark at strategic positions
        if len(text) > 100:
            # Embed at multiple points for redundancy
            mid = len(text) // 2
            quarter = len(text) // 4
            
            return (text[:quarter] + watermark + 
                    text[quarter:mid] + watermark + 
                    text[mid:] + watermark)
        else:
            # Single watermark at end
            return text + watermark
    
    @classmethod
    def extract_watermark(cls, text: str) -> Optional[str]:
        """Extract and decode watermark from text"""
        try:
            # Extract zero-width characters
            zero_width_chars = ''.join(
                c for c in text 
                if c in [cls.ZERO_WIDTH_SPACE, cls.ZERO_WIDTH_NON_JOINER]
            )
            
            if not zero_width_chars:
                return None
            
            binary = cls._zero_width_to_binary(zero_width_chars)
            return cls._binary_to_text(binary)
        except:
            return None
    
    @classmethod
    def verify_watermark(cls, text: str) -> bool:
        """Verify that text contains valid creator watermark"""
        try:
            extracted = cls.extract_watermark(text)
            if not extracted:
                return False
            
            # Check if it contains creator signature
            return "Abdul Rashid Dickson" in extracted or "ARD:" in extracted
        except:
            return False
    
    @classmethod
    def get_attribution_metadata(cls) -> Dict[str, Any]:
        """Get attribution metadata for API responses"""
        return {
            "_attribution": {
                "creator": "Abdul Rashid Dickson",
                "signature": _WATERMARK_SIGNATURE,
                "copyright": "© 2025 Abdul Rashid Dickson",
                "project": "AKOO AI - Advanced PDF Intelligence Platform",
                "timestamp": int(time.time()),
                "hash": hashlib.sha256(
                    f"{_WATERMARK_CREATOR}:{time.time()}".encode()
                ).hexdigest()[:16]
            }
        }
    
    @classmethod
    def watermark_dict(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Add watermark metadata to dictionary responses"""
        if not isinstance(data, dict):
            return data
        
        # Add hidden attribution
        result = data.copy()
        result.update(cls.get_attribution_metadata())
        
        # Add signature to any text fields
        if 'summary' in result and isinstance(result['summary'], str):
            result['summary'] = cls.embed_watermark(result['summary'])
        
        return result


class FileProtector:
    """File-level protection with hash verification"""
    
    # Files that must contain creator attribution
    PROTECTED_PATTERNS = [
        "Abdul Rashid Dickson",
        "Created by:",
        "AKOO AI",
        _WATERMARK_SIGNATURE
    ]
    
    @classmethod
    def generate_file_hash(cls, filepath: str) -> str:
        """Generate SHA-256 hash of file contents"""
        try:
            with open(filepath, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except:
            return ""
    
    @classmethod
    def verify_attribution_present(cls, filepath: str) -> bool:
        """Verify that file contains required attribution"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Must contain at least one protected pattern
            for pattern in cls.PROTECTED_PATTERNS:
                if pattern in content:
                    return True
            
            return False
        except:
            return True  # Can't read = don't block
    
    @classmethod
    def add_file_header(cls, content: str, file_type: str = "python") -> str:
        """Add protected header to file content"""
        if file_type == "python":
            header = '''"""
╔══════════════════════════════════════════════════════════════════════════════╗
║     AKOO AI - Advanced PDF Intelligence Platform                            ║
║     Created by: Abdul Rashid Dickson                                        ║
║     © 2025 All Rights Reserved                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

'''
        elif file_type == "javascript":
            header = '''/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║     AKOO AI - Advanced PDF Intelligence Platform                            ║
 * ║     Created by: Abdul Rashid Dickson                                        ║
 * ║     © 2025 All Rights Reserved                                              ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 */

'''
        elif file_type == "html":
            header = '''<!--
╔══════════════════════════════════════════════════════════════════════════════╗
║     AKOO AI - Advanced PDF Intelligence Platform                            ║
║     Created by: Abdul Rashid Dickson                                        ║
║     © 2025 All Rights Reserved                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
-->

'''
        elif file_type == "css":
            header = '''/*
╔══════════════════════════════════════════════════════════════════════════════╗
║     AKOO AI - Advanced PDF Intelligence Platform                            ║
║     Created by: Abdul Rashid Dickson                                        ║
║     © 2025 All Rights Reserved                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
*/

'''
        else:
            header = f"/* Created by: Abdul Rashid Dickson - © 2025 */\n\n"
        
        return header + content


# Export watermarking functions
def watermark_summary(summary: str) -> str:
    """Watermark a summary text"""
    return Watermark.embed_watermark(summary)

def watermark_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """Watermark an API response"""
    return Watermark.watermark_dict(response)

def get_creator_attribution() -> Dict[str, Any]:
    """Get creator attribution data"""
    return Watermark.get_attribution_metadata()


# Auto-verify on import
if __name__ != "__main__":
    # Verify this file hasn't been tampered with
    if "Abdul Rashid Dickson" not in open(__file__, 'r', encoding='utf-8').read():
        raise RuntimeError("Watermark module integrity compromised - Created by Abdul Rashid Dickson")
