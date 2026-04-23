"""
RMI Tools Bundle
All external tools self-contained - no shell pulling needed

Quick access:
    from rmi.tools import maigret, deepface, social_analyzer, munchscan
    
Or use the OSINT wrapper:
    from rmi.integrations.osint_tools import search_username, verify_faces
"""

# Import paths for easy access
MAIGRET_DATA_DIR = __path__[0] + "/maigret"
DEEPCHECK_WEIGHTS_DIR = __path__[0] + "/deepface/weights"
SOCIAL_ANALYZER_DIR = __path__[0] + "/social_analyzer"
MUNCHSCAN_DIR = __path__[0] + "/munchscan"
OPENCODE_DIR = __path__[0] + "/../integrations/ai_tools/opencode"
KIMI_CONFIG_DIR = __path__[0] + "/../integrations/ai_tools/kimi_cli"

__all__ = [
    "MAIGRET_DATA_DIR",
    "DEEPCHECK_WEIGHTS_DIR", 
    "SOCIAL_ANALYZER_DIR",
    "MUNCHSCAN_DIR",
    "OPENCODE_DIR",
    "KIMI_CONFIG_DIR"
]
