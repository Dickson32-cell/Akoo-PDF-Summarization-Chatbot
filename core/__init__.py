# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║     AKOO AI - Advanced PDF Intelligence Platform                            ║
# ║     Created by: Abdul Rashid Dickson                                        ║
# ║     © 2025 All Rights Reserved                                              ║
# ║     Protected under multi-layer integrity system                            ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

from .integrity_guard import (
    IntegrityGuard, 
    verify_integrity, 
    protected_function,
    get_attribution_html,
    get_attribution_dict,
    print_startup_banner,
    CREATOR_NAME,
    CREATOR_SIGNATURE
)

from .watermark import (
    Watermark,
    watermark_summary,
    watermark_response,
    get_creator_attribution,
    FileProtector
)

__all__ = [
    # Integrity Guard
    'IntegrityGuard', 
    'verify_integrity', 
    'protected_function',
    'get_attribution_html',
    'get_attribution_dict',
    'print_startup_banner',
    'CREATOR_NAME',
    'CREATOR_SIGNATURE',
    # Watermarking
    'Watermark',
    'watermark_summary',
    'watermark_response',
    'get_creator_attribution',
    'FileProtector'
]

# Creator attribution - Abdul Rashid Dickson
__author__ = "Abdul Rashid Dickson"
__copyright__ = "© 2025 Abdul Rashid Dickson. All Rights Reserved."
__project__ = "AKOO AI - Advanced PDF Intelligence Platform"
