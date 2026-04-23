"""
RMI AI Tools Integration
Self-contained AI/ML tools - no external shell dependencies

Quick access:
    from rmi.integrations.ai_tools import kimi, opencode
    
    # Kimi (me!)
    kimi("analyze this code", yolo=True)
    kimi_interactive()  # Start interactive session
    
    # Opencode
    launch_opencode()   # Launch TUI
    launch_web()        # Launch web interface
"""

from .opencode_launcher import (
    OpencodeLauncher,
    launch_opencode,
    launch_web,
    opencode_version
)

from .kimi_launcher import (
    KimiLauncher,
    kimi,
    kimi_interactive,
    kimi_version,
    kimi_config
)

__all__ = [
    # Opencode
    "OpencodeLauncher",
    "launch_opencode",
    "launch_web",
    "opencode_version",
    # Kimi
    "KimiLauncher",
    "kimi",
    "kimi_interactive",
    "kimi_version",
    "kimi_config"
]
